package com.automation.api.service;

import com.automation.api.model.Task;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class TaskService {
    private final Map<String, Task> tasks = new ConcurrentHashMap<>();
    private final RestTemplate restTemplate;
    
    @Value("${llm.service.url}")
    private String llmServiceUrl;

    public TaskService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Task executeTask(Task task) {
        // First, consult LLM service for task execution strategy
        Map<String, Object> llmResponse = restTemplate.postForObject(
            llmServiceUrl + "/analyze",
            Map.of("task", task, "action", "execute"),
            Map.class
        );

        if (llmResponse != null && (Boolean)llmResponse.get("requires_code_generation")) {
            // Let LLM generate and deploy new code
            return handleDynamicExecution(task, llmResponse);
        }

        // Default execution logic
        task.setStatus("in_progress");
        tasks.put(task.getId().toString(), task);
        
        new Thread(() -> {
            try {
                Thread.sleep(5000);
                task.setStatus("completed");
            } catch (InterruptedException e) {
                task.setStatus("failed");
            }
        }).start();
        
        return task;
    }

    private Task handleDynamicExecution(Task task, Map<String, Object> llmResponse) {
        try {
            // Get generated code from LLM
            Map<String, Object> codeGenResponse = restTemplate.postForObject(
                llmServiceUrl + "/generate",
                Map.of("task", task, "context", llmResponse),
                Map.class
            );

            if (codeGenResponse != null && (Boolean)codeGenResponse.get("success")) {
                // Execute the dynamically generated code
                return executeDynamicCode(task, codeGenResponse);
            }
        } catch (Exception e) {
            task.setStatus("failed");
            task.setDescription("Failed to generate/execute dynamic code: " + e.getMessage());
        }
        return task;
    }

    private Task executeDynamicCode(Task task, Map<String, Object> codeGenResponse) {
        try {
            // Execute the generated code through LLM service
            Map<String, Object> executionResponse = restTemplate.postForObject(
                llmServiceUrl + "/execute",
                Map.of("task", task, "code", codeGenResponse.get("code")),
                Map.class
            );

            if (executionResponse != null && (Boolean)executionResponse.get("success")) {
                task.setStatus("completed");
                task.setDescription(executionResponse.get("result").toString());
            } else {
                task.setStatus("failed");
                task.setDescription("Dynamic execution failed");
            }
        } catch (Exception e) {
            task.setStatus("failed");
            task.setDescription("Error during dynamic execution: " + e.getMessage());
        }
        return task;
    }

    public Task getTaskStatus(String taskId) {
        Task task = tasks.get(taskId);
        if (task == null) {
            throw new RuntimeException("Task not found");
        }
        return task;
    }
} 