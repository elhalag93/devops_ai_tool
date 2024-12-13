<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>Automation Platform</title>
    <link rel="stylesheet" href="static/css/main.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Automation Platform</h1>
            <nav>
                <ul>
                    <li><a href="#dashboard">Dashboard</a></li>
                    <li><a href="#chat">Chat Interface</a></li>
                    <li><a href="#tasks">Tasks</a></li>
                    <li><a href="#configuration">Configuration</a></li>
                </ul>
            </nav>
        </header>

        <main>
            <section id="dashboard" class="dashboard-container">
                <!-- Dashboard content will be loaded here -->
            </section>

            <section id="chat" class="chat-container">
                <div class="chat-messages" id="chatMessages"></div>
                <div class="chat-input">
                    <input type="text" id="userInput" placeholder="Type your command...">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </section>
        </main>
    </div>

    <script src="static/js/main.js"></script>
</body>
</html> 