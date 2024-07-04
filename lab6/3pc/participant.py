import random
import logging

# coordinator messages
from const3PC import PREPARE_COMMIT, VOTE_REQUEST, GLOBAL_COMMIT, GLOBAL_ABORT
# participant decissions
from const3PC import LOCAL_SUCCESS, LOCAL_ABORT
# participant messages
from const3PC import READY_COMMIT, VOTE_COMMIT, VOTE_ABORT
# misc constants
from const3PC import TIMEOUT

import stablelog


class Participant:
    """
    Implements a two phase commit participant.
    - state written to stable log (but recovery is not considered)
    - in case of coordinator crash, participants mutually synchronize states
    - system blocks if all participants vote commit and coordinator crashes
    - allows for partially synchronous behavior with fail-noisy crashes
    """

    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log(
            "participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.2pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.state = 'NEW'

    @staticmethod
    def _do_work():
        # Simulate local activities that may succeed or not
        return LOCAL_ABORT if random.random() > 2/3 else LOCAL_SUCCESS

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Participant {} entered state {}."
                         .format(self.participant, state))
        self.state = state

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self._enter_state('INIT')  # Start in local INIT state.

    def run(self):
        # Wait for start of joint commit
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)
        if not msg:  # Crashed coordinator - give up entirely
            # decide to locally abort (before doing anything)
            self._enter_state('ABORT')
            return "Participant {} terminated in state {} due to Coordinator Crash.".format(
            self.participant, self.state)

        else:  # Coordinator requested to vote, joint commit starts
            assert msg[1] == VOTE_REQUEST
            # Firstly, come to a local decision
            # if self.participant == min(self.all_participants):  # simulate a crash
            #     return "Participant {} crashed in state INIT after VOTE_REQUEST.".format(self.participant)

            decision = self._do_work()  # proceed with local activities
            # If local decision is negative,
            # then vote for abort and quit directly
            if decision == LOCAL_ABORT:
                self.channel.send_to(self.coordinator, VOTE_ABORT)

            # If local decision is positive,
            # we are ready to proceed the joint commit
            else:
                assert decision == LOCAL_SUCCESS
                self._enter_state('READY')
                
                # Notify coordinator about local commit vote
                self.channel.send_to(self.coordinator, VOTE_COMMIT)

                # if self.participant == min(self.all_participants):  # simulate a crash
                #     return "Participant {} crashed in state Ready after VOTE_COMMIT.".format(self.participant)

                # Wait for coordinator to notify the final outcome
                msg = self.channel.receive_from(self.coordinator, TIMEOUT)
                if not msg:  # Crashed coordinator
                    min_id = min(self.all_participants)
                    self.coordinator = {min_id}
                    if self.participant == min_id:
                        decision = self.coordinator_work()
                        return "Coordinator {} terminated in state {} due to {}.".format(
                            self.participant, self.state, decision)
                    else:
                        self.help_coordinator()
                        if decision != LOCAL_ABORT:
                            msg = self.channel.receive_from(self.coordinator, TIMEOUT * 2)
                            decision = msg[1]
                        else:
                            return "Coordinator {} terminated in state {} due to {}.".format(
                                self.participant, self.state, decision)
                else:  # Coordinator came to a decision
                    if decision != LOCAL_ABORT:
                        decision = msg[1]

        # Change local state based on the outcome of the joint commit protocol
        # Note: If the protocol has blocked due to coordinator crash,
        # we will never reach this point
        if decision == PREPARE_COMMIT:
            self._enter_state('PRECOMMIT')
            self.channel.send_to(self.coordinator, READY_COMMIT)
        elif decision == GLOBAL_ABORT:
            if self.state != 'ABORT':
                self._enter_state('ABORT')
            return "Participant {} terminated in state {} due to {}.".format(
                self.participant, self.state, decision)
        else:
            if self.state != 'ABORT':
                self._enter_state('ABORT')
            msg = self.channel.receive_from(self.coordinator, TIMEOUT)
            if not msg:  # Crashed coordinator
                min_id = min(self.all_participants)
                self.coordinator = {min_id}
                if self.participant == min_id:
                    decision = self.coordinator_work()
                    return "Coordinator {} terminated in state {} due to {}.".format(
                        self.participant, self.state, decision)
                else:
                    self.help_coordinator()
                    if decision != LOCAL_ABORT:
                        msg = self.channel.receive_from(self.coordinator, TIMEOUT * 2)
                        decision = msg[1]
            else:
                return "Participant {} terminated in state {} due to {}.".format(
                        self.participant, self.state, decision)
            
        # Wait for coordinator to notify the final outcome 
        msg = self.channel.receive_from(self.coordinator, TIMEOUT * 2)
        if not msg:  # Crashed coordinator
            min_id = min(self.all_participants)
            self.coordinator = {min_id}
            if self.participant == min_id:
                decision = self.coordinator_work()
                return "Coordinator {} terminated in state {} due to {}.".format(
                    self.participant, self.state, decision)
            else:
                self.help_coordinator()
                if decision != LOCAL_ABORT:
                    msg = self.channel.receive_from(self.coordinator, TIMEOUT * 2)
                    decision = msg[1]
        else:  # Coordinator came to a decision
            if decision != LOCAL_ABORT:
                decision = msg[1]

        if decision == GLOBAL_COMMIT:
            self._enter_state('COMMIT')
        else:
            assert decision in [GLOBAL_ABORT, LOCAL_ABORT]
            if self.state != 'ABORT':
                self._enter_state('ABORT')

        return "Participant {} terminated in state {} due to {}.".format(
            self.participant, self.state, decision)

    def coordinator_work(self):
        self.logger.info("Participant {} is the new Coordinator."
            .format(self.participant))
        if self.state == 'READY':
            self._enter_state('WAIT')
            # Inform all participants about own state
            self.channel.send_to(self.all_participants, 'WAIT')
            if self.state != 'ABORT':
                self._enter_state('ABORT')
            self.channel.send_to(self.all_participants, GLOBAL_ABORT)
            return GLOBAL_ABORT
        elif self.state == 'PRECOMMIT':
            # Inform all participants about own state
            self.channel.send_to(self.all_participants, 'PRECOMMIT')
            self._enter_state('COMMIT')
            self.channel.send_to(self.all_participants, GLOBAL_COMMIT)
            return GLOBAL_COMMIT
        elif self.state == 'ABORT':
            # Inform all participants about own state
            self.channel.send_to(self.all_participants, 'ABORT')
            if self.state != 'ABORT':
                self._enter_state('ABORT')
            self.channel.send_to(self.all_participants, GLOBAL_ABORT)
            return GLOBAL_ABORT
        else:
            # Inform all participants about own state
            self.channel.send_to(self.all_participants, 'COMMIT')
            self.channel.send_to(self.all_participants, GLOBAL_COMMIT)
            return GLOBAL_COMMIT

    def help_coordinator(self):
        msg = self.channel.receive_from(self.coordinator, TIMEOUT * 2)
        if msg[1] == 'WAIT' and self.state == 'INIT':
            self._enter_state('READY')
        elif msg[1] == 'PRECOMMIT' and self.state == 'READY':
            self._enter_state('PRECOMMIT')
        elif msg[1] == 'COMMIT' and self.state != 'COMMIT':
            self._enter_state('COMMIT')
        elif msg[1] == 'ABORT' and self.state != 'ABORT':
            self._enter_state('ABORT')