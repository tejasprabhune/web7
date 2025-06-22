"use client";
import PlanList from "@/components/planlist";
import { ParticlesComponent } from "./particles";
import { Spotlight } from "./spotlight";
import { useAgentData } from "./hooks/useAgentData";

export default function App() {
	const agentData = useAgentData();
	
	return (
		<div>
			<ParticlesComponent />
			<Spotlight 
				agentData={agentData}
			/>
			<PlanList 
				agentId={agentData.agentId}
				actionPlan={agentData.actionPlan}
				agentData={agentData}
				isMarkovActive={false}
				nodeCount={0}
			/>
		</div>
	);
}
