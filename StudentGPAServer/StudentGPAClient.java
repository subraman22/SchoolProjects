/**
 * Simple single threaded client for the StudentGPAServer. Supports int keys and float values.
 * Operations are Put(key, value), Get(key), and Delete(key)
 * CS 6650 Scalable Distributed Systems
 * Spring 2020 Project 1
 * 2/3/20
 * by Rohan Subramaniam
 */

import java.io.*;
import java.net.*;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Scanner;

/**
 * Wrapper class just for the main method to run the right protocol client
 */
public class StudentGPAClient {
    /**
     * Main method for running the correct protocol client
     * @param args Protocol, Host name or IP, and port number
     */
    public static void main(String[] args) {
        if (args.length != 3) {
            System.out.println("Invalid input. Usage: java -jar Project1Client.jar <Protocol> <HostName/IP> <port>");
        }
        int port = 8080;
        try {
            port = Integer.parseInt(args[2]);
        } catch (NumberFormatException e) {
            System.out.println("Invalid port argument. Port number must be an int");
        }
        InetAddress host = null;
        String hostName = args[1];
        if (validateIP(hostName)) {
            try {
                host = InetAddress.getByAddress(hostName.getBytes());
            } catch (UnknownHostException e) {
                System.out.println("UnknownHostException while validating IP");
            }
        } else {
            try {
                host = InetAddress.getByName(hostName);
            } catch (UnknownHostException e) {
                System.out.println("Unknown/invalid Host. Could not connect");
            }
        }

        if (args[0].equalsIgnoreCase("TCP")) {
                TCPClient client = new TCPClient(port, host);
                Thread clientThread = new Thread(client);
                clientThread.start();

        } else if (args[0].equalsIgnoreCase("UDP")) {
                UDPClient client = new UDPClient(port, host);
                Thread clientThread = new Thread(client);
                clientThread.start();

        } else {
            System.out.println("Invalid protocol argument. Must be UDP or TCP");
        }
    }

    /**
     * Regex referenced from https://stackoverflow.com/questions/5667371/validate-ipv4-address-in-java
     * @param ip string version of IP address
     * @return
     */
    private static boolean validateIP (final String ip) {
        String ipRegex =
                "^((0|1\\d?\\d?|2[0-4]?\\d?|25[0-5]?|[3-9]\\d?)\\.){3}(0|1\\d?\\d?|2[0-4]?\\d?|25[0-5]?|[3-9]\\d?)$";

        return ip.matches(ipRegex);
    }
}

/**
 * TCP protocol version of the GPA client
 */
class TCPClient implements Runnable {
    private int port = 8080;
    private InetAddress host = null;
    private String hostName = null;


    /**
     * Constructor that takes a string host name and port number
     * @param port int
     * @param hostName String name of host
     * @throws UnknownHostException if the host name is invalid
     */
    public TCPClient(int port, String hostName) throws UnknownHostException {
        this.port = port;
        this.hostName = hostName;
        this.host = InetAddress.getByName(hostName);
    }

    /**
     * Constructor that takes an InetAddress IP.
     * @param port int
     * @param hostIP IP address of host
     */
    public TCPClient(int port, InetAddress hostIP) {
        this.host = hostIP;
        this.port = port;
    }

    /**
     * Empty Constructor
     */
    public TCPClient() {}

    /**
     * Thread's run method that opens the input and output streams, takes user input and sends it to the server, then
     * listens for the response
     */
    @Override
    public void run() {
        try {
            Socket client = new Socket(this.host, this.port);  // Create the client socket

            // Create the output and input communication streams
            OutputStream clientOut = client.getOutputStream();
            DataOutputStream dataOutStream = new DataOutputStream(clientOut);
            InputStream clientIn = client.getInputStream();
            DataInputStream dataInStream = new DataInputStream(clientIn);

            populateHashMap(dataInStream, dataOutStream);

            Scanner keyboard = new Scanner(System.in);  // Once populated, create a scanner to take user input

            boolean running = true;
            while (running) {
                // Take user input to send to the server
                System.out.print(timestamp() + "Enter text: ");
                String message = keyboard.nextLine();
                if (message.equalsIgnoreCase("exit")) {
                    running = false;
                }

                dataOutStream.writeUTF(message);

                // Read the response from the server and print it
                String returnMessage = dataInStream.readUTF();
                System.out.println(timestamp() + returnMessage);
            }

            // Close everything
            keyboard.close();
            dataInStream.close();
            dataOutStream.close();
            clientIn.close();
            clientOut.close();
            client.close();

        } catch (IOException e) {
            System.out.println("Couldn't connect to server");
            System.exit(1);
        }
    }

    /**
     * Populates the hash map on the server by sending five put requests before asking for user input
     * @param dataIn DataInputStream from server
     * @param dataOut DataOutputStream to server
     */
    private void populateHashMap(DataInputStream dataIn, DataOutputStream dataOut) {
        ArrayList<String> commands = new ArrayList<>(5);
        commands.add("PUT(1000, 3.86)");
        commands.add("PUT(1001, 2.45)");
        commands.add("PUT(1002, 4.0)");
        commands.add("PUT(1003, 3.25)");
        commands.add("PUT(1995, 1.16)");

        try {
            for (String command : commands) {
                dataOut.writeUTF(command);

                // Read the response from the server and print it
                String returnMessage = dataIn.readUTF();
                System.out.println(timestamp() + returnMessage);
            }
        } catch (IOException e) {
            System.out.println(timestamp() + "Error while entering initial values");
        }
    }

    /**
     * Timestamp of the current time to print on each line.
     * @return String version of the timestamp formatted for readability
     */
    private String timestamp() {
        long currentTime = System.currentTimeMillis();
        DateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:ms");
        //formatted value of current Date
        String time = "" + df.format(currentTime);
        return "(System time: " + time + ") ";
    }
}

/**
 * UDP protocol version of the GPA server
 */
class UDPClient implements Runnable {
    private int port = 8080;
    private InetAddress host = null;
    private String hostName = null;

    /**
     * Constructor that takes a string host name
     * @param port int
     * @param hostName String
     * @throws UnknownHostException if invalid host name is given
     */
    public UDPClient(int port, String hostName) throws UnknownHostException {
        this.port = port;
        this.hostName = hostName;
        this.host = InetAddress.getByName(hostName);
    }

    /**
     * Constructor that takes an IP address along with the port number
     * @param port int
     * @param hostIP InetAddress
     */
    public UDPClient(int port, InetAddress hostIP) {
        this.port = port;
        this.host = hostIP;
        this.hostName = host.getHostName();
    }

    /**
     * Empty Constructor
     */
    public UDPClient() {}

    /**
     * Thread's run method that establishes the Datagram socket and sends/receives DatagramPackets with the server
     */
    @Override
    public void run() {
        DatagramSocket socket = null;
        try {
            socket = new DatagramSocket();  // Create the client socket

            populateHashMap(socket);

            Scanner keyboard = new Scanner(System.in);

            boolean running = true;
            while (running) {
                // Take user input to send to the server
                System.out.print(timestamp() + "Enter text: ");
                String messageString = keyboard.nextLine();
                if (messageString.equalsIgnoreCase("exit")) {
                    running = false;
                }
                byte[] messageBytes = messageString.getBytes();
                InetAddress host = InetAddress.getByName(hostName);
                DatagramPacket request = new DatagramPacket(messageBytes, messageBytes.length, host, port);
                socket.send(request);
                byte[] buffer = new byte[1000];
                DatagramPacket returnMessage = new DatagramPacket(buffer, buffer.length);
                socket.setSoTimeout(10000);  // Ten second timeout for unresponsive server

                try {
                    socket.receive(returnMessage);
                } catch (SocketTimeoutException e) {
                    System.out.println(timestamp() + "No response from server. Request timed out");
                }

                // Read the response from the server once it has been reversed and print it

                System.out.println(timestamp() + new String(returnMessage.getData()));
            }

            // Close everything
            keyboard.close();

        } catch (IOException e) {
            System.out.println("Couldn't connect to server");
            System.exit(1);
        }
    }

    /**
     * Populates the server's hashmap with five entries by sending five put commands before taking user input
     * @param socket DatagramSocket
     */
    private void populateHashMap(DatagramSocket socket) {
        ArrayList<String> commands = new ArrayList<>(5);
        commands.add("PUT(1000, 3.86)");
        commands.add("PUT(1001, 2.45)");
        commands.add("PUT(1002, 4.0)");
        commands.add("PUT(1003, 3.25)");
        commands.add("PUT(1995, 1.16)");

        try {
            for (String command : commands) {

                byte[] messageBytes = command.getBytes();
                InetAddress host = InetAddress.getByName(hostName);
                DatagramPacket request = new DatagramPacket(messageBytes, messageBytes.length, host, port);
                socket.send(request);
                byte[] buffer = new byte[1000];
                DatagramPacket returnMessage = new DatagramPacket(buffer, buffer.length);
                socket.setSoTimeout(10000);  // Ten second timeout for unresponsive server

                try {
                    socket.receive(returnMessage);
                } catch (SocketTimeoutException e) {
                    System.out.println(timestamp() + "No response from server. Request timed out");
                }
                // Read the response from the server and print it

                System.out.println(timestamp() + new String(returnMessage.getData()));
            }
        } catch (IOException e) {
            System.out.println(timestamp() + "Error while entering initial values");
        }
    }

    /**
     * Timestamp of the current time to print on each line.
     * @return String version of the timestamp formatted for readability
     */
    private String timestamp() {
        long currentTime = System.currentTimeMillis();
        DateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:ms");
        //formatted value of current Date
        String time = "" + df.format(currentTime);
        return "(System time: " + time + ") ";
    }
}