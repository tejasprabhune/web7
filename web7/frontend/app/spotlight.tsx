"use client";

import { useState, useEffect } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import { Command } from "cmdk";
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	DialogDescription,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ReactFlowProvider } from 'reactflow';
import { MarkovChainFlow } from '@/components/MarkovChain/MarkovChainFlow';
import { useMarkovChain } from '@/components/MarkovChain/useMarkovChain';
import { MarkovNode } from '@/components/MarkovChain/types';
import PlanList from '@/components/planlist';
import StreamingDetails from "@/components/StreamingDetails";

interface SpotlightProps {
	agentData: {
		agentId: string | null;
		actionPlan: { steps: any[] } | null;
		currentStep: string | null;
		stepResponse: any | null;
		stepHistory: string[];
		isPolling: boolean;
		startPolling: () => void;
		stopPolling: () => void;
		createAgent: (query: string) => Promise<string | null>;
		resetData: () => void;
		setCurrentStepId: (id: string | null) => void;
		isLoading: boolean;
		error: string | null;
	};
}

export function Spotlight({ agentData }: SpotlightProps) {
	const [open, setOpen] = useState(false);
	const [search, setSearch] = useState("");
	const [showVisualization, setShowVisualization] = useState(false);

	useHotkeys("mod+k", (e) => {
		e.preventDefault();
		if (!open) {
			setOpen(true);
		} else {
			// If closing the dialog, reset everything
			resetState();
		}
	});

	const {
		nodes,
		edges,
		addNode,
		clearNodes,
	} = useMarkovChain({
		stepResponse: agentData.stepResponse,
		actionPlan: agentData.actionPlan,
		currentStepId: agentData.currentStep,
		onStepComplete: agentData.setCurrentStepId,
	});

	// When the action plan is loaded, set the current step to the first one.
	useEffect(() => {
		if (agentData.actionPlan && !agentData.currentStep) {
			const firstStepId = agentData.actionPlan.steps?.[0]?.id;
			if (firstStepId) {
				agentData.setCurrentStepId(firstStepId);
			}
		}
	}, [agentData.actionPlan, agentData.currentStep, agentData.setCurrentStepId]);

	// Start polling only when the action plan and current step are available.
	useEffect(() => {
		if (agentData.actionPlan && agentData.currentStep) {
			agentData.startPolling();
		}
	}, [agentData.actionPlan, agentData.currentStep, agentData.startPolling]);

	// Stop polling when all steps are completed by comparing node count to plan length
	useEffect(() => {
		if (agentData.actionPlan?.steps && agentData.isPolling) {
			if (nodes.length >= agentData.actionPlan.steps.length) {
				agentData.stopPolling();
			}
		}
	}, [nodes.length, agentData.actionPlan, agentData.isPolling, agentData.stopPolling]);

	const resetState = () => {
		setShowVisualization(false);
		agentData.stopPolling();
		clearNodes();
		setSearch("");
		setOpen(false);
		agentData.resetData();
	};

	const handleEnter = async () => {
		if (!showVisualization) {
			// First Enter press - show visualization
			setShowVisualization(true);
			// Make initial API call to get agent ID. The useEffect above will handle starting the polling.
			await agentData.createAgent(search);
		} else {
			// Second Enter press - close everything and reset
			resetState();
		}
	};

	const handleOpenChange = (isOpen: boolean) => {
		if (!isOpen) {
			// If dialog is closed by any means (e.g., Escape key), reset state
			resetState();
		} else {
			setOpen(true);
		}
	};

	return (
		<Dialog
			open={open}
			onOpenChange={handleOpenChange}
		>
			<DialogContent className="p-0 overflow-hidden w-[90vw] max-w-[95vw] bg-transparent border-none shadow-none" showCloseButton={false}>
				{!showVisualization ? (
					// Search interface
					<>
						<DialogHeader className="px-4 pt-4 mx-auto w-64">
							<DialogTitle></DialogTitle>
							<DialogDescription></DialogDescription>
						</DialogHeader>
						<Command>
							<Input
								autoFocus
								className="w-[50vw] mx-auto bg-muted text-foreground placeholder:text-muted-foreground border-none p-4"
								placeholder={agentData.isLoading ? "Creating agent..." : "What do you want to do today?"}
								value={search}
								onChange={(e) => setSearch(e.target.value)}
								onKeyDown={(e) => {
									if (e.key === 'Enter' && !agentData.isLoading) {
										handleEnter();
									}
								}}
								disabled={agentData.isLoading}
							/>
						</Command>
					</>
				) : (
					// Visualization interface
					<ReactFlowProvider>
						<div className="flex h-[85vh] w-full bg-white rounded-lg overflow-hidden">
							{/* Left Panel */}
							<div className="w-[25%] flex-shrink-0 bg-white flex flex-col border-r border-gray-200">
								<div className="h-[50%]">
									<PlanList 
										isMarkovActive={agentData.isPolling || nodes.length > 0}
										nodeCount={nodes.length}
										agentId={agentData.agentId}
										actionPlan={agentData.actionPlan}
										agentData={agentData}
									/>
								</div>
								<div className="h-[50%]">
									<StreamingDetails stepHistory={agentData.stepHistory} isPolling={agentData.isPolling} />
								</div>
							</div>
							
							{/* Markov Chain */}
							<div className="flex-1 bg-gray-50">
								<MarkovChainFlow
									nodes={nodes}
									edges={edges}
									className="h-full w-full"
								/>
							</div>
						</div>
					</ReactFlowProvider>
				)}
			</DialogContent>
		</Dialog>
	);
}
