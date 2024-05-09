Aufgabe 3.1: Client -> Server
Sobald der Client gestartet ist sendet diese die erste Nachricht. Der Client ist bis zur Ankunft einer Antwort blockiert. Sobald der Server gestartet wird, wird die erste Nachricht geprintet und dem Client eine Antwort gesendet. Es geht keine Nachricht verloren. Nachdem der Client alle 3 Nachrichten gesendet und entsprechende Antworten geprintet hat wird der Server nach einer kleinen Verzögerung beendet.
Client -> Client1 -> Server
Die Funktionsweise ist wie zuvor. Jedoch diesmal mit zusätzlich Client1. Der Server Bearbeitet erst die Nachrichten vom Client und anschließend die vom Client1.

Aufgabe 3.2: Server -> Client -> Client
Der Server schickt seinen Subscriber entweder einen String mit Time oder Date. Dies ist davon abhängig was der Client abonniert hat. Hierbei abonnieren die Clients Time und printen diese 5-mal. Anschließend schließen diese. Der Server sende diese unendlich lange, somit ist es möglich, dass wenn der eine Client eine Nachricht empfangen hat und anschließend der nächste gestartet wird, die Ausgaben mit vier Ausgaben übereinstimmen. Jedoch beim ersten Client die erste Nachricht eine andere ist als beim zweiten. Der zweite Client enthält hat eine andere letzte Nachricht empfangen als der erste Client.

Server -> Client -> Client1
Hier ist das verhalten das gleich wie zuvor. Jedoch gibt es hier statt eines zweiten Clients einen Client1. Dieser hat das Date abonniert und gibt dieses 3-mal aus bevor dieser beendet wird.

Aufgabe 3.3: Farmer -> Farmer -> Worker
Die beiden Farmer (tasksrc) warten darauf das der Worker gestartet wird und anschließend senden diese ihm eine zufällige Zahl von 1 bis 100. Dieser druckt die erhaltenen Zahlen anschließend in einem String aus. Dabei handelt es sich insgesamt um 200 Zahlen die der Worker erhält. Der Worker verarbeitet die erhalten Nachrichten gleichverteilt. Erst wird ein Wert von einem Farmer gedruckt und anschließend vom anderen und dieses wechselt sich so lange ab, bis alle Zahlen gedruckt sind.
Worker -> Worker -> Farmer
Nachdem die Worker gestartet sind warten diese auf eine Nachricht vom Farmer. Sobald der Farmer gestartet ist sendet dieser den Worker die zufälligen Zahlen wie im vorherigen Beispiel. Jedoch werden die zwischen den Workern aufgeteilt.


