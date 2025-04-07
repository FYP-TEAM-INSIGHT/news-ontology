import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.CRFClassifier;
import edu.stanford.nlp.ling.CoreLabel;
import org.json.JSONObject;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.stream.Collectors;

public class NERServer {
    // Default port
    private static final int DEFAULT_PORT = 8000;
    // Default classifier path
    private static final String DEFAULT_CLASSIFIER = "classifiers/english.all.3class.distsim.crf.ser.gz";

    public static void main(String[] args) throws Exception {
        // Parse command line arguments for port and classifier
        int port = DEFAULT_PORT;
        String classifierPath = DEFAULT_CLASSIFIER;

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("-port") && i + 1 < args.length) {
                port = Integer.parseInt(args[i + 1]);
                i++;
            } else if (args[i].equals("-classifier") && i + 1 < args.length) {
                classifierPath = args[i + 1];
                i++;
            }
        }

        // Load the classifier
        System.out.println("Loading classifier: " + classifierPath);
        AbstractSequenceClassifier<CoreLabel> classifier = CRFClassifier.getClassifier(classifierPath);

        // Create HTTP server
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        // Create context for NER API endpoint
        server.createContext("/api/ner", new NERHandler(classifier));

        // Start the server
        server.start();
        System.out.println("NER Server started on port " + port);
        System.out.println("Send POST requests to http://localhost:" + port + "/api/ner with JSON body: {\"message\": \"your text here\"}");
    }

    static class NERHandler implements HttpHandler {
        private final AbstractSequenceClassifier<CoreLabel> classifier;

        public NERHandler(AbstractSequenceClassifier<CoreLabel> classifier) {
            this.classifier = classifier;
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            try {
                // Only support POST method
                if (!exchange.getRequestMethod().equals("POST")) {
                    sendResponse(exchange, 405, "Method Not Allowed. Use POST.");
                    return;
                }

                // Read request body
                String requestBody = new BufferedReader(new InputStreamReader(exchange.getRequestBody(), StandardCharsets.UTF_8))
                        .lines()
                        .collect(Collectors.joining("\n"));

                // Parse JSON
                JSONObject jsonRequest;
                try {
                    jsonRequest = new JSONObject(requestBody);
                } catch (Exception e) {
                    sendResponse(exchange, 400, "Invalid JSON format");
                    return;
                }

                // Extract message
                if (!jsonRequest.has("message")) {
                    sendResponse(exchange, 400, "Missing 'message' field in request");
                    return;
                }

                String text = jsonRequest.getString("message");

                // Process text with NER
                String format = jsonRequest.optString("format", "inlineXML");
                String result = processText(text, format);

                // Create JSON response
                JSONObject jsonResponse = new JSONObject();
                jsonResponse.put("result", result);

                // Send response
                sendResponse(exchange, 200, jsonResponse.toString());
            } catch (Exception e) {
                e.printStackTrace();
                sendResponse(exchange, 500, "Internal Server Error: " + e.getMessage());
            }
        }

        private String processText(String text, String format) {
            switch (format) {
                case "slashTags":
                    return classifier.classifyToString(text, "slashTags", false);
                case "xml":
                    return classifier.classifyToString(text, "xml", true);
                case "tsv":
                    return classifier.classifyToString(text, "tsv", false);
                case "tabbedEntities":
                    return classifier.classifyToString(text, "tabbedEntities", false);
                case "inlineXML":
                default:
                    return classifier.classifyWithInlineXML(text);
            }
        }

        private void sendResponse(HttpExchange exchange, int statusCode, String response) throws IOException {
            exchange.getResponseHeaders().add("Content-Type", "application/json");
            exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
            exchange.sendResponseHeaders(statusCode, response.getBytes(StandardCharsets.UTF_8).length);

            try (OutputStream os = exchange.getResponseBody()) {
                os.write(response.getBytes(StandardCharsets.UTF_8));
            }
        }
    }
}