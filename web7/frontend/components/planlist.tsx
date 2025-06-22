"use client";

import { useState, useEffect, useRef } from "react";
import { Menu, CheckCircle, Clock, Circle, X } from "lucide-react";

type TaskStatus = "completed" | "in-progress" | "not-started";

interface TaskItem {
  id: string;
  title: string;
  status: TaskStatus;
}

interface PlanListProps {
  isMarkovActive?: boolean;
  nodeCount?: number;
  agentId?: string | null;
  actionPlan?: { steps: any[] } | null;
  agentData?: {
    agentId: string | null;
    actionPlan: { steps: any[] } | null;
    isLoading: boolean;
    error: string | null;
  };
}

export default function PlanList({ isMarkovActive = false, nodeCount = 0, agentId, actionPlan, agentData }: PlanListProps) {
  const [isOpen, setIsOpen] = useState(true); // Default to open in side-by-side mode
  const [tasks, setTasks] = useState<TaskItem[]>([]);

  const toggleTaskStatus = (taskId: string) => {
    setTasks(prevTasks => 
      prevTasks.map(task => {
        if (task.id === taskId) {
          const statusOrder: TaskStatus[] = ["not-started", "in-progress", "completed"];
          const currentIndex = statusOrder.indexOf(task.status);
          const nextIndex = (currentIndex + 1) % statusOrder.length;
          return { ...task, status: statusOrder[nextIndex] };
        }
        return task;
      })
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "updated":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "started":
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case "not_started":
        return <Circle className="w-5 h-5 text-gray-400" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "updated":
        return "text-green-600";
      case "started":
        return "text-yellow-600";
      case "not_started":
        return "text-gray-400";
      default:
        return "text-gray-400";
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">Plan</h2>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="text-white hover:text-blue-100 transition-colors"
          >
            {isOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
        <p className="text-blue-100 text-xs mt-1">
          {actionPlan?.steps?.filter(t => t.status === "updated").length} of {agentData?.actionPlan?.steps?.length} completed
        </p>
        {agentData?.isLoading && !agentData.actionPlan && (
          <p className="text-blue-100 text-xs mt-1">
            Loading action plan...
          </p>
        )}
        {agentData?.error && (
          <p className="text-red-200 text-xs mt-1">
            Error: {agentData.error}
          </p>
        )}
        {isMarkovActive && (
          <p className="text-blue-100 text-xs mt-1">
            Nodes: {nodeCount}/{agentData?.actionPlan?.steps.length}
          </p>
        )}
      </div>

      {/* Task List */}
      {isOpen && (
        <div className="flex-1 overflow-y-auto">
          <ul className="p-3 space-y-2">
            {actionPlan?.steps?.map((step: any) => (
              <li
                key={step.id}
                className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors duration-150 cursor-pointer group"
                onClick={() => toggleTaskStatus(step.id)}
              >
                <div className="flex-shrink-0">
                  {getStatusIcon(step.status)}
                </div>
                <span className={`flex-1 text-sm font-medium ${getStatusColor(step.status)} group-hover:text-gray-900 transition-colors duration-150`}>
                  {step.name}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Footer */}
      {isOpen && (
        <div className="border-t border-gray-100 px-3 py-2 bg-gray-50">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Status</span>
            <span>{actionPlan?.steps?.filter(t => t.status === "started").length} in progress</span>
          </div>
        </div>
      )}
    </div>
  );
}
