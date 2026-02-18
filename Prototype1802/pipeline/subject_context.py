from __future__ import annotations

SUBJECT_MAP = {
    "operating systems": {
        "core_units": [
            "Processes & Threads",
            "CPU Scheduling (FCFS, SJF, RR, Priority)",
            "Synchronization (Critical Section, Mutex, Semaphores, Monitors)",
            "Deadlocks (conditions, prevention, avoidance, detection)",
            "Memory Management (paging, segmentation, virtual memory)",
            "File Systems basics",
        ],
        "common_questions": [
            "Explain process vs thread with diagram",
            "Compare scheduling algorithms with examples",
            "Deadlock conditions + Banker’s algorithm numericals",
            "Critical section + semaphore solutions (Dining Philosophers, Readers-Writers)",
            "Paging/virtual memory numericals: page faults, replacement",
        ],
        "exam_signals": [
            "If professor stresses ‘deadlock’ → expect Banker’s / wait-for graph",
            "If stresses ‘synchronization’ → expect semaphore code + invariants",
            "If stresses ‘scheduling’ → expect Gantt chart problems",
        ],
    },
    "data structures": {
        "core_units": [
            "Arrays, Strings",
            "Stacks & Queues",
            "Linked Lists",
            "Trees (BST, AVL basics)",
            "Heaps / Priority Queue",
            "Hashing",
            "Graphs (BFS/DFS, shortest path basics)",
            "Sorting & Searching",
        ],
        "common_questions": [
            "Stack/Queue applications",
            "Linked list operations + complexity",
            "Tree traversals + BST insert/delete",
            "Heap operations",
            "Hash collisions + probing",
            "BFS/DFS trace",
            "Compare sorts: Quick/Merge/Heap, stability, complexity",
        ],
        "exam_signals": [
            "If prof gives lots of trace problems → expect dry-runs",
            "If prof emphasizes complexity → expect compare/justify questions",
        ],
    },
}


def generate_subject_context(subject: str) -> str:
    s = (subject or "").strip().lower()
    if not s:
        return (
            "No subject provided.\n"
            "Fallback mode: I will output a generic exam plan and ask for syllabus."
        )

    if s in SUBJECT_MAP:
        d = SUBJECT_MAP[s]
        return (
            f"KNOWN SUBJECT: {subject}\n\n"
            f"Core units:\n- " + "\n- ".join(d["core_units"]) + "\n\n"
            f"Common exam questions:\n- " + "\n- ".join(d["common_questions"]) + "\n\n"
            f"Signals / professor hints mapping:\n- " + "\n- ".join(d["exam_signals"])
        )

    # unknown subject: do NOT hallucinate random school topics
    return (
        f"UNKNOWN SUBJECT: {subject}\n\n"
        "Strict behavior:\n"
        "- I will NOT invent a syllabus.\n"
        "- I will output a generic scoring strategy framework.\n"
        "- For accurate predictions, add syllabus/notes/past papers."
    )
