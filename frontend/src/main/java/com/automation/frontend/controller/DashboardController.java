package com.automation.frontend.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class DashboardController {

    @GetMapping("/")
    public String dashboard(Model model) {
        model.addAttribute("pageTitle", "Automation Platform");
        return "dashboard";
    }

    @GetMapping("/chat")
    public String chat(Model model) {
        model.addAttribute("pageTitle", "Chat Interface");
        return "chat";
    }

    @GetMapping("/tasks")
    public String tasks(Model model) {
        model.addAttribute("pageTitle", "Task Management");
        return "tasks";
    }
} 