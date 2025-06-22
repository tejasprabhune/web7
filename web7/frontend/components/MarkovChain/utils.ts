import { MarkovNode, NodePosition } from './types';

// Check if two nodes would overlap
const checkCollision = (pos1: NodePosition, pos2: NodePosition, nodeWidth: number = 140, nodeHeight: number = 80): boolean => {
  const margin = 75; // Extra margin between nodes
  return !(
    pos1.x + nodeWidth + margin < pos2.x ||
    pos2.x + nodeWidth + margin < pos1.x ||
    pos1.y + nodeHeight + margin < pos2.y ||
    pos2.y + nodeHeight + margin < pos1.y
  );
};

// Find a non-overlapping position
const findNonOverlappingPosition = (
  desiredPosition: NodePosition,
  existingNodes: MarkovNode[],
  containerWidth: number,
  containerHeight: number,
  maxAttempts: number = 20
): NodePosition => {
  const nodeWidth = 140;
  const nodeHeight = 80;
  const margin = 100;
  
  // Try the desired position first
  if (!existingNodes.some(node => 
    node.x !== undefined && node.y !== undefined && 
    checkCollision(desiredPosition, { x: node.x, y: node.y }, nodeWidth, nodeHeight)
  )) {
    return desiredPosition;
  }
  
  // Try random positions around the desired position
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const offsetX = (Math.random() - 0.5) * 300; // Random offset within 300px
    const offsetY = (Math.random() - 0.5) * 100; // Smaller vertical offset
    
    const testPosition = {
      x: desiredPosition.x + offsetX,
      y: desiredPosition.y + offsetY,
    };
    
    // Ensure within bounds
    testPosition.x = Math.max(margin, Math.min(containerWidth - margin - nodeWidth, testPosition.x));
    testPosition.y = Math.max(margin, Math.min(containerHeight - margin - nodeHeight, testPosition.y));
    
    // Check if this position doesn't overlap with any existing nodes
    if (!existingNodes.some(node => 
      node.x !== undefined && node.y !== undefined && 
      checkCollision(testPosition, { x: node.x, y: node.y }, nodeWidth, nodeHeight)
    )) {
      return testPosition;
    }
  }
  
  // If all attempts fail, return the desired position (fallback)
  return desiredPosition;
};

export const calculateNodePosition = (
  node: MarkovNode,
  containerWidth: number,
  containerHeight: number,
  timeRange: { min: number; max: number },
  existingNodes: MarkovNode[] = [],
  parentNode?: MarkovNode
): NodePosition => {
  const margin = 100;
  const nodeHeight = 100; // Increased spacing between nodes
  const maxHorizontalOffset = 200; // Increased horizontal spread
  
  let desiredX: number;
  let desiredY: number;
  
  if (parentNode && parentNode.x !== undefined && parentNode.y !== undefined) {
    // Position below the parent node with random horizontal offset
    desiredY = parentNode.y + nodeHeight;
    
    // Add random horizontal offset, but keep it within bounds
    const horizontalOffset = (Math.random() - 0.5) * maxHorizontalOffset;
    desiredX = parentNode.x + horizontalOffset;
    
    // Ensure the node stays within bounds
    desiredX = Math.max(margin, Math.min(containerWidth - margin - 140, desiredX));
  } else {
    // First node or no parent - position at the top with some randomness
    desiredX = containerWidth / 2 + (Math.random() - 0.5) * 300; // Increased random offset
    desiredY = containerHeight * 0.2; // Start a bit lower to leave room above
    
    // Ensure the node stays within bounds
    desiredX = Math.max(margin, Math.min(containerWidth - margin - 140, desiredX));
  }
  
  // Ensure the node stays within vertical bounds
  desiredY = Math.max(margin, Math.min(containerHeight - margin - 80, desiredY));
  
  const desiredPosition = { x: desiredX, y: desiredY };
  
  // Find a non-overlapping position
  return findNonOverlappingPosition(desiredPosition, existingNodes, containerWidth, containerHeight);
};

export const getTimeRange = (nodes: MarkovNode[]) => {
  if (nodes.length === 0) return { min: 0, max: 1 };
  
  const timestamps = nodes.map(node => node.timestamp);
  return {
    min: Math.min(...timestamps),
    max: Math.max(...timestamps)
  };
};

export const generateNodeId = (timestamp: number, index: number) => 
  `node-${timestamp}-${index}`;

export const generateEdgeId = (sourceId: string, targetId: string) => 
  `edge-${sourceId}-${targetId}`;

// Get the last N nodes in a lineage
export const getLastNodesInLineage = (nodes: MarkovNode[], count: number = 3): MarkovNode[] => {
  if (nodes.length <= count) return nodes;
  return nodes.slice(-count);
};

// Calculate the viewport to show exactly the last 3 nodes with space for the next one
export const calculateViewportForLastNodes = (
  nodes: MarkovNode[], 
  containerWidth: number, 
  containerHeight: number,
  count: number = 3
) => {
  const lastNodes = getLastNodesInLineage(nodes, count);
  if (lastNodes.length === 0) return null;
  
  const positions = lastNodes.map(node => ({ x: node.x || 0, y: node.y || 0 }));
  const minX = Math.min(...positions.map(p => p.x));
  const maxX = Math.max(...positions.map(p => p.x));
  const minY = Math.min(...positions.map(p => p.y));
  const maxY = Math.max(...positions.map(p => p.y));
  
  // Calculate center point of the visible nodes
  const centerX = (minX + maxX) / 2;
  
  // Position viewport to show the last 3 nodes with space below for the next one
  // The viewport should be positioned so that the 3rd node from the end is at the top
  // and there's space below for the next node to appear
  const nodeHeight = 100;
  const viewportCenterY = maxY - (nodeHeight * 1.5); // Position to show last 3 nodes with space below
  
  // Calculate zoom to fit the horizontal spread with generous padding
  const horizontalSpread = Math.max(maxX - minX, 400); // Increased for larger nodes
  const padding = 180; // Increased padding for larger nodes
  
  const zoom = Math.min(
    (containerWidth - 2 * padding) / horizontalSpread,
    0.8 // Fixed zoom level for consistent viewport size
  );
  
  return {
    x: centerX,
    y: viewportCenterY,
    zoom: Math.max(zoom, 0.6) // Minimum zoom to ensure good visibility
  };
};

// Shift all nodes up when a new node is added to maintain 3-node viewport
export const shiftNodesUp = (nodes: MarkovNode[], shiftAmount: number = 100): MarkovNode[] => {
  return nodes.map(node => ({
    ...node,
    y: node.y !== undefined ? node.y - shiftAmount : node.y,
  }));
}; 