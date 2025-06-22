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
    fetchActionPlan: (agentId: string) => Promise<number | null>;
    isLoading: boolean;
    error: string | null;
  };
}

export default function PlanList({ isMarkovActive = false, nodeCount = 0, agentId, actionPlan, agentData }: PlanListProps) {
  const [isOpen, setIsOpen] = useState(true); // Default to open in side-by-side mode
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [isPolling, setIsPolling] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef(false);

  // Poll for action plan updates when agent is active
  useEffect(() => {
    if (!agentId || !agentData || isPollingRef.current) return;

    // Clear any existing polling
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }

    isPollingRef.current = true;
    setIsPolling(true);
    const pollInterval = 10000; // Poll every 10 seconds (increased)

    const pollForUpdates = async () => {
      if (!isPollingRef.current) return;
      
      const status = await agentData.fetchActionPlan(agentId);
      
      // Stop polling if status is 0 (complete) or if there was an error
      if (status === 0 || status === null) {
        console.log('Action plan complete or error occurred, stopping polling');
        isPollingRef.current = false;
        setIsPolling(false);
        return;
      }
      
      pollingRef.current = setTimeout(pollForUpdates, pollInterval);
    };

    // Start polling
    pollForUpdates();

    return () => {
      isPollingRef.current = false;
      setIsPolling(false);
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [agentId]); // Only depend on agentId

  // Auto-progress tasks based on Markov chain activity
  useEffect(() => {
    if (isMarkovActive) {
      setTasks(prevTasks => {
        const newTasks = [...prevTasks];
        
        // Progress based on node count
        if (nodeCount >= 1) {
          newTasks[0] = { ...newTasks[0], status: "completed" };
          newTasks[1] = { ...newTasks[1], status: "completed" };
        }
        
        // if (nodeCount >= 2) {
        //   newTasks[2] = { ...newTasks[2], status: "in-progress" };
        // }
        
        // if (nodeCount >= 3) {
        //   newTasks[2] = { ...newTasks[2], status: "completed" };
        //   newTasks[3] = { ...newTasks[3], status: "in-progress" };
        // }
        
        // if (nodeCount >= 4) {
        //   newTasks[3] = { ...newTasks[3], status: "completed" };
        //   newTasks[4] = { ...newTasks[4], status: "completed" };
        // }
        
        return newTasks;
      });
    }
  }, [isMarkovActive, nodeCount]);

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

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "in-progress":
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case "not-started":
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case "completed":
        return "text-green-600";
      case "in-progress":
        return "text-yellow-600";
      case "not-started":
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
          {tasks.filter(t => t.status === "completed").length} of {tasks.length} completed
        </p>
        {agentData?.isLoading && (
          <p className="text-blue-100 text-xs mt-1">
            Loading action plan...
          </p>
        )}
        {isPolling && (
          <p className="text-blue-100 text-xs mt-1">
            🔄 Polling for updates...
          </p>
        )}
        {!isPolling && agentId && (
          <p className="text-green-200 text-xs mt-1">
            ✅ Action plan complete
          </p>
        )}
        {agentData?.error && (
          <p className="text-red-200 text-xs mt-1">
            Error: {agentData.error}
          </p>
        )}
        {isMarkovActive && (
          <p className="text-blue-100 text-xs mt-1">
            Nodes: {nodeCount}/15
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
            <span>{tasks.filter(t => t.status === "in-progress").length} in progress</span>
          </div>
        </div>
      )}
    </div>
  );
}
