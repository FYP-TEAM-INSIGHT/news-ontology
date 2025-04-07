FROM maven:3.9.9-eclipse-temurin-21

# Set working directory
WORKDIR /app

# Copy all 
COPY . .

# Compile the server
RUN javac -cp "stanford-ner.jar:lib/*:." NERServer.java

# Expose the port the server runs on
EXPOSE 8000

# Command to run the server
CMD ["java", "-cp", "stanford-ner.jar:lib/*:.", "-mx1g", "NERServer"]