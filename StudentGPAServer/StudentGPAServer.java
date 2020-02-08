/**
 * Simple single threaded HashMap server. Supports int keys and float values.
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
import java.util.HashMap;

public class StudentGPAServer {
    /**
     * Main method to run the correct type of server on a specified port
     * @param args Protocol and Port number
     */
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Invalid input. Usage: java -jar Project1Server.jar <Protocol> <Port>");
        }
        int port = 8080;
        try {
            port = Integer.parseInt(args[1]);
        } catch (NumberFormatException e) {
            System.out.println("Invalid port argument. Port number must be an int");
            System.exit(1);
        }

        // Start the correct protocol server thread
        if (args[0].equalsIgnoreCase("TCP")) {
            TCPServer server = new TCPServer(port);
            Thread serverThread = new Thread(server);
            serverThread.start();

        } else if (args[0].equalsIgnoreCase("UDP")) {
            UDPServer server = new UDPServer(port);
            Thread serverThread = new Thread(server);
            serverThread.start();

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
 * TCP version of the GPA server
 */
class TCPServer implements Runnable {
    private int port = 8080;
    private ServerSocket serverSocket = null;
    protected Thread runningThread = null;
    private HashMap<Integer, Float> dictionary = new HashMap<>();

    /**
     * Constructor that can change the port
     * @param port int port number
     */
    public TCPServer(int port) {
        this.port = port;
    }

    /**
     * Empty Constructor
     */
    public TCPServer() {}

    /**
     * Overrides the run method for Runnable. Opens the server socket, listens for a client connection, and handles
     * the client request when it is issued. Continues to handle requests indefinitely until killed
     */
    @Override
    public void run() {
        synchronized (this) {
            runningThread = Thread.currentThread();
        }
        try { // Open server socket
            serverSocket = new ServerSocket(port);
        } catch (IOException e) {
            System.out.println("Error connecting to port");
            System.exit(1);
        }

        // Listen and handle requests as long as it has not stopped
        while(true) {
            Socket client = null;
            try {
                client = serverSocket.accept();
            } catch (IOException e) {
                System.out.println("Error accepting client connection");
                System.exit(1);
            }
            String clientIP = client.getInetAddress().getHostAddress();

            // Instantiate all of the IO streams
            InputStream in = null;
            OutputStream out = null;
            DataOutputStream dataOut = null;
            DataInputStream dataIn = null;

            // Try to open the IO streams
            try {
                in = client.getInputStream();
                out = client.getOutputStream();
                dataOut = new DataOutputStream(out);
                dataIn = new DataInputStream(in);
            } catch (IOException e) {
                System.out.println("Error getting IO streams");
            }
            // Once the client connection has been confirmed established, handle all of its requests
            boolean clientConnected = true;
            while(clientConnected) {
                try {
                    handleRequest(dataIn, dataOut, clientIP);
                } catch (IOException e) {
//                    System.out.println("IOException while handling the request");
                    clientConnected = false;
                }
            }

            // Try to close the IO streams
            try {
                dataIn.close();
                dataOut.close();
                in.close();
                out.close();
            } catch (IOException e) {
                System.out.println("IOException while closing streams");
            } catch (NullPointerException e) {
                System.out.println("NullPointerException while closing streams");
            }
        }
    }

    /**
     * Handles a single request from the client and returns a response
     * @param dataIn DataInputStream wrapped input stream
     * @param dataOut DataOutputStream wrapped output stream
     * @param clientIP String representation of client IP address
     * @throws IOException if client is not available
     */
    private void handleRequest(DataInputStream dataIn, DataOutputStream dataOut, String clientIP) throws IOException {
        String message = dataIn.readUTF();
        String response = "None";
        System.out.println(timestamp() + "Message received from IP " + clientIP + ": " + message);
        String[] params = message.split("[( ),]+");

        // Check for the command type and executes the appropriate one
        if (params[0].equalsIgnoreCase("put") && params.length == 3) {  // Check for put and 2 args
            try {
                put(Integer.parseInt(params[1]), Float.parseFloat(params[2]));
                response = "Successful put";
            } catch (NumberFormatException e) {
                response = "Key must be int. Value must be float";
            }
        } else if (params[0].equalsIgnoreCase("get") && params.length == 2) {  // Check for get and 1 arg
            try {
                Float val = get(Integer.parseInt(params[1]));
                response = val.toString();
            } catch (NullPointerException e) {
                response = "Key not found";
            } catch (NumberFormatException e) {
                response = "Key must be an int";
            }
        } else if (params[0].equalsIgnoreCase("delete") && params.length == 2) {  // Check for delete 1 arg
            try {
                boolean success = delete(Integer.parseInt(params[1]));
                response = success ? "Key deleted" : "Key not found";
            } catch (NumberFormatException e) {
                response = "Key must be an int";
            }
        } else if (params[0].equalsIgnoreCase("exit")) {  // Check if the client is exiting
            System.out.println(timestamp() + "Client is exiting");
            response = "Confirmed client exit. Server still running";
        } else {
            response = "Invalid command. Command must be PUT(K, V), GET(K), or DELETE(K)";
        }

        System.out.println(timestamp() + "Response to client: " + response);

        dataOut.writeUTF("Response: " + response);
    }

    /**
     * Wrapper for putting values into the hash map
     * @param key int ID number
     * @param value float GPA
     */
    private void put(int key, float value) {
        dictionary.put(key, value);
    }

    /**
     * Wrapper for the hash map get
     * @param key int to get
     * @return float value
     */
    private float get(int key) {
        return dictionary.get(key);
    }

    /**
     * Wrapper to remove key/value pairs from the hash map
     * @param key int to delete
     * @return boolean Successful or not
     */
    private boolean delete(int key) {
        if (!dictionary.containsKey(key)) {
            return false;
        } else {
            dictionary.remove(key);
            return true;
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
class UDPServer implements Runnable {
    private int port = 8080;
    private DatagramSocket serverSocket = null;
    protected Thread runningThread = null;
    private HashMap<Integer, Float> dictionary = new HashMap<>();

    /**
     * Constructor that can change the port
     * @param port int port number
     */
    public UDPServer(int port) {
        this.port = port;
    }

    /**
     * Empty Constructor
     */
    public UDPServer() {}

    /**
     * Overrides the run method for Runnable. Opens the server socket, listens for a client connection, and handles
     * the client request when it is issued. Continues to handle requests indefinitely until killed
     */
    @Override
    public void run() {
        synchronized (this) {
            runningThread = Thread.currentThread();
        }
        try { // Open server socket
            serverSocket = new DatagramSocket(port);
        } catch (IOException e) {
            System.out.println("Error connecting to port");
            System.exit(1);
        }

        byte[] buffer = new byte[1000];
        // Listen and handle requests as long as it has not stopped
        while(true) {
            DatagramPacket request = new DatagramPacket(buffer, buffer.length);
            String message = "No Message";

            // Receive a message
            try {
                serverSocket.receive(request);
                message = new String(request.getData(), request.getOffset(), request.getLength());
            } catch (IOException e) {
                System.out.println("Error accepting client connection");
                System.exit(1);
            }
            String clientIP = request.getAddress().getHostAddress();

            // Create and send the response
            byte[] response = handleRequest(message, clientIP);
            DatagramPacket responsePacket = new DatagramPacket(response, response.length,
                    request.getAddress(), request.getPort());

            try {
                serverSocket.send(responsePacket);
            } catch (IOException e) {
                System.out.println("Error sending response packet");
            }

        }
    }

    /**
     * Handles a single request from the client. Checks the type of command, executes it, and responds to the client
     * @param message String from client
     * @param clientIP String form of the client IP address
     * @return Byte array response to be sent back to the client
     */
    private byte[] handleRequest(String message, String clientIP) {
        String response;
        System.out.println(timestamp() + "Message received from IP " + clientIP + ": " + message);
        String[] params = message.split("[( ),]+");

        // Check for the command type and executes the appropriate one
        if (params[0].equalsIgnoreCase("put") && params.length == 3) {  // Check for put and 2 args
            try {
                put(Integer.parseInt(params[1]), Float.parseFloat(params[2]));
                response = "Successful put";
            } catch (NumberFormatException e) {
                response = "Key must be int. Value must be float";
            }
        } else if (params[0].equalsIgnoreCase("get") && params.length == 2) {  // Check for get and 1 arg
            try {
                Float val = get(Integer.parseInt(params[1]));
                response = val.toString();
            } catch (NullPointerException e) {
                response = "Key not found";
            } catch (NumberFormatException e) {
                response = "Key must be an int";
            }
        } else if (params[0].equalsIgnoreCase("delete") && params.length == 2) {  // Check for delete 1 arg
            try {
                boolean success = delete(Integer.parseInt(params[1]));
                response = success ? "Successfully deleted" : "Key not found";
            } catch (NumberFormatException e) {
                response = "Key must be an int";
            }

        } else if (params[0].equalsIgnoreCase("exit")) {  // Check if the client is exiting
            System.out.println(timestamp() + "Client is exiting");
            response = "Confirmed client exit. Server still running";

        } else {
            response = "Invalid command";
        }

        System.out.println(timestamp() + "Sending response to IP " + clientIP + ": " + response);
        return ("Response: " + response).getBytes();
    }

    /**
     * Wrapper for putting values into the hash map
     * @param key int ID number
     * @param value float GPA
     */
    private void put(int key, float value) {
        dictionary.put(key, value);
    }

    /**
     * Wrapper for the hash map get
     * @param key int to get
     * @return float value
     */
    private float get(int key) {
        return dictionary.get(key);
    }

    /**
     * Wrapper to remove key/value pairs from the hash map
     * @param key int to delete
     * @return boolean Successful or not
     */
    private boolean delete(int key) {
        if (!dictionary.containsKey(key)) {
            return false;
        } else {
            dictionary.remove(key);
            return true;
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
