"use client";

import React, { useEffect, useState } from 'react';
import { ReactFlowProvider } from 'reactflow';
import { MarkovChainFlow } from '@/components/MarkovChain/MarkovChainFlow';
import { useMarkovChain } from '@/components/MarkovChain/useMarkovChain';
import { MarkovNode } from '@/components/MarkovChain/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function MarkovChainPage() {
  const [selectedNode, setSelectedNode] = useState<MarkovNode | null>(null);
  const [customNodeLabel, setCustomNodeLabel] = useState('');

  const {
    nodes,
    edges,
    startPolling,
    stopPolling,
    addNode,
    clearNodes,
    isPolling,
  } = useMarkovChain({
    pollingInterval: 3000,
    maxNodes: 30,
    onNewNode: (node) => {
      console.log('New node added:', node);
    },
    onNewEdge: (edge) => {
      console.log('New edge added:', edge);
    },
  });

  const handleNodeClick = (node: MarkovNode) => {
    setSelectedNode(node);
  };

  const handleAddCustomNode = () => {
    if (customNodeLabel.trim()) {
      addNode(customNodeLabel.trim());
      setCustomNodeLabel('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Markov Chain Visualization
          </h1>
          <p className="text-gray-600">
            Real-time animated visualization of a Markov chain with nodes appearing over time
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Controls Panel */}
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Controls</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-col space-y-2">
                  <Button
                    onClick={isPolling ? stopPolling : startPolling}
                    variant={isPolling ? "destructive" : "default"}
                    className="w-full"
                  >
                    {isPolling ? 'Stop Polling' : 'Start Polling'}
                  </Button>
                  
                  <Button
                    onClick={clearNodes}
                    variant="outline"
                    className="w-full"
                  >
                    Clear All Nodes
                  </Button>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Add Custom Node
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={customNodeLabel}
                      onChange={(e) => setCustomNodeLabel(e.target.value)}
                      placeholder="Enter node label"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onKeyPress={(e) => e.key === 'Enter' && handleAddCustomNode()}
                    />
                    <Button
                      onClick={handleAddCustomNode}
                      size="sm"
                      disabled={!customNodeLabel.trim()}
                    >
                      Add
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Nodes:</span>
                  <span className="text-sm font-medium">{nodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Edges:</span>
                  <span className="text-sm font-medium">{edges.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium ${isPolling ? 'text-green-600' : 'text-gray-600'}`}>
                    {isPolling ? 'Polling' : 'Idle'}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Selected Node Info */}
            {selectedNode && (
              <Card>
                <CardHeader>
                  <CardTitle>Selected Node</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Label:</span>
                    <span className="text-sm font-medium">{selectedNode.label}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">ID:</span>
                    <span className="text-sm font-medium">{selectedNode.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Timestamp:</span>
                    <span className="text-sm font-medium">
                      {new Date(selectedNode.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {selectedNode.data && (
                    <div className="pt-2 border-t">
                      <span className="text-sm text-gray-600">Data:</span>
                      <pre className="text-xs mt-1 p-2 bg-gray-50 rounded">
                        {JSON.stringify(selectedNode.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Flow Visualization */}
          <div className="lg:col-span-3">
            <Card className="h-[600px]">
              <CardHeader>
                <CardTitle>Markov Chain Flow</CardTitle>
              </CardHeader>
              <CardContent className="p-0 h-full">
                <ReactFlowProvider>
                  <MarkovChainFlow
                    nodes={nodes}
                    edges={edges}
                    onNodeClick={handleNodeClick}
                    className="h-full"
                  />
                </ReactFlowProvider>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 