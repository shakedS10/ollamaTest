digraph AbstractFileAnalysis {
    rankdir=LR;
    node [shape=box, fontname="Arial", fontsize=10];
    
    subgraph cluster0 {
        label="Abstract File Analysis Flow";
        style=dashed;
        color=gray;

        User [label="User / Input Source"];
        Receive [label="1) Input File Reception"];
        Identify [label="2) File Identification & Pre-Processing\n- Determine file type\n- Extract basic metadata\n- Quick AV / Hash check"];
        StaticAnalysis [label="3) Static Analysis\n- File-specific checks (PDF, EXE, etc.)\n- Produce static risk flags/scores"];
        LLMAnalysis [label="4) LLM-based Content Analysis\n- Extract text/content\n- LLM classification (safe/suspicious)"];
        Sandbox [label="5) Optional Dynamic Sandbox Analysis\n- Execute/parse in sandbox\n- Collect behavior indicators"];
        Aggregation [label="6) Aggregation & Decision\n- Combine static, LLM,\n  and dynamic signals"];
        Output [label="7) Output & Logging\n- Final verdict (Safe, Malicious)\n- Log results"];

        // Define the flow
        User -> Receive -> Identify -> StaticAnalysis -> LLMAnalysis -> Sandbox -> Aggregation -> Output;
    }
}
