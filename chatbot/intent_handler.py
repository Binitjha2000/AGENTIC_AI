import os
import json
import numpy as np
import subprocess
import logging
from typing import Dict, Tuple, List

class IntentHandler:
    def __init__(self, cache, kb, generator):
        self.cache = cache
        self.kb = kb
        self.generator = generator
        self.logger = logging.getLogger(__name__)
        self.flows = {}
        self._load_intents()

    def _load_intents(self):
        """Load and validate intents"""
        with open("intents.json") as f:
            data = json.load(f)
            self.intents = data["intents"]
            self.intent_embeddings = self._precompute_embeddings()
            
            # Validate required fields
            for intent in self.intents:
                if not all(k in intent for k in ["tag", "patterns"]):
                    self.logger.warning(f"Invalid intent format: {intent}")

    def _precompute_embeddings(self):
        """Generate intent embeddings with validation"""
        embeddings = []
        for intent in self.intents:
        # Validate script path exists
            if "script" in intent:
                if not os.path.exists(intent["script"]):
                    self.logger.warning(f"Script not found: {intent['script']}")

        for intent in self.intents:
            if not intent.get("patterns"):
                self.logger.error(f"Intent {intent['tag']} has no patterns")
                continue
                
            embeddings.append({
                "tag": intent["tag"],
                "script": intent.get("script"),
                "flow": intent.get("flow", []),
                "embedding": np.mean([
                    self.cache.get_embedding(p)
                    for p in intent["patterns"]
                ], axis=0)
            })
        return embeddings

    def _run_script(self, script_path: str, params: dict = None) -> str:
    # Convert to absolute path
        abs_path = os.path.abspath(script_path)
    
        if not os.path.exists(abs_path):
            return f"Script not found at: {abs_path}"
        
        try:
            cmd = ["python", abs_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                shell=True,  # Required for paths with spaces on Windows
                check=True  # Raise exception on non-zero exit
            )
            return result.stdout.strip() or "Script executed successfully"
        except subprocess.CalledProcessError as e:
            return f"Script failed (code {e.returncode}): {e.stderr}"
        except Exception as e:
            return f"Execution error: {str(e)}"

    def classify_intent(self, query: str) -> Dict:
        query_embed = self.cache.get_embedding(query)
        query_norm = query_embed / np.linalg.norm(query_embed)
    
        best_match = None
        max_sim = -1
    
        for intent in self.intent_embeddings:
            intent_embed = intent["embedding"]
            intent_norm = intent_embed / np.linalg.norm(intent_embed)
            similarity = np.dot(query_norm, intent_norm)  # Cosine similarity
        
            if similarity > max_sim:
                max_sim = similarity
                best_match = intent
            
        return {**best_match, "confidence": float(max_sim)}

    def handle_query(self, query: str, session_id: str, mode: str) -> Tuple[str, str]:
        """Handle query with enhanced RAG integration"""
        try:
            if mode == "kb":
                rag_results = self.kb.search(query)
                if not rag_results:
                    return "No relevant documentation found. Try rephrasing.", "knowledge"
                return self.generator.enhance_rag_response(query, rag_results), "knowledge"
            
            if session_id in self.flows:
                return self._continue_flow(session_id, query)
                
            intent = self.classify_intent(query)
            
            if intent["confidence"] < 0.5:
                return "Could not determine intent. Please provide more details.", "clarify"
                
            if intent["flow"]:
                return self._start_flow(intent["flow"], session_id)
                
            if intent["script"]:
                output = self._run_script(intent["script"])
                #return self.generator.humanize(f"{intent['tag']}:\n{output}"), "action"
                return f"{intent['tag']}:\n{output}", "action"
                
            return "I need more information to resolve this issue.", "clarify"
            
        except Exception as e:
            self.logger.error(f"Handler error: {str(e)}")
            return self.generator.humanize("System error occurred"), "error"

    def _start_flow(self, flow: List[Dict], session_id: str) -> Tuple[str, str]:
        """Initialize troubleshooting flow"""
        self.flows[session_id] = {
            "current_step": 0,
            "answers": {},
            "flow": flow,
            "start_time": time.time()
        }
        first_step = flow[0]
        return (
            f"## {first_step['question']}\n{first_step.get('hint', '')}",
            "flow_question",
            first_step.get("options", [])
        )

    def _continue_flow(self, session_id: str, answer: str) -> Tuple[str, str]:
        """Progress through troubleshooting flow"""
        flow_state = self.flows.get(session_id)
        if not flow_state:
            return "Session expired. Please start over.", "error"
            
        current_step = flow_state["flow"][flow_state["current_step"]]
        flow_state["answers"][current_step["key"]] = answer
        
        next_step_index = flow_state["current_step"] + 1
        if next_step_index < len(flow_state["flow"]):
            flow_state["current_step"] = next_step_index
            next_step = flow_state["flow"][next_step_index]
            return (
                f"## {next_step['question']}\n{next_step.get('hint', '')}",
                "flow_question",
                next_step.get("options", [])
            )
            
        # Execute final script with collected parameters
        del self.flows[session_id]
        try:
            output = self._run_script(
                flow_state["flow"][-1]["script"],
                flow_state["answers"]
            )
            return self.generator.humanize(output), "action"
        except Exception as e:
            return f"Failed to execute resolution: {str(e)}", "error"