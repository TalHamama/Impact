import { NODES, EDGES } from "../data/mockData";

export const apiService = {
    fetchGraphData: async () => {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));
        return {
            nodes: NODES,
            edges: EDGES
        };
    },

    reportIncident: async (nodeId, incident) => {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        console.log(`Reported incident for ${nodeId}:`, incident);
        return { success: true };
    }
};
