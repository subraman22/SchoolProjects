CS 6650 Scalable Distributed Systems
Spring 2020 Project 1
2/3/20
by Rohan Subramaniam

This project is a simple single-threaded server and client that I chose to make store studentGPAs. As it is now, there
are no checks for valid ID numbers or valid GPAs, the point of the project was to begin familiarizing us with socket
programming. The Keys for the HashMap are int studentIDs and the Values are float GPAs

TO RUN:
1. Start the server using java -jar StudentGPAServer.jar <Protocol> <Port>
    Protocol should be TCP or UDP. Port should be an int
2. Start the client using java -jar StudentGPAClient.jar <Protocol> <Hostname/IP> <Port>
    Protocol should be the same as the server. Testing done using localhost and port 8080
3. Enter commands in the client window followed by enter. Commands are PUT(key, value), GET(key), and DELETE(key)
4. To close the client, enter "exit" as the command
5. The server will run indefinitely until killed from outside