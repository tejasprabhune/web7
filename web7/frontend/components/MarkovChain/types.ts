export interface MarkovNode {
  id: string;
  label: string;
  timestamp: number;
  data?: any;
  x?: number;
  y?: number;
}

export interface MarkovEdge {
  id: string;
  source: string;
  target: string;
  timestamp: number;
}

export interface NodePosition {
  x: number;
  y: number;
}

export interface MarkovChainState {
  nodes: MarkovNode[];
  edges: MarkovEdge[];
  currentTime: number;
} 