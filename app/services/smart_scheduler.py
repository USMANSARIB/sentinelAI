import time
import heapq
import config

class SearchTerm:
    def __init__(self, term, bucket, base_priority):
        self.term = term
        self.bucket = bucket
        self.base_priority = base_priority
        self.current_multiplier = 1.0
        self.last_scraped_at = 0.0

    def calculate_urgency(self, current_time):
        """
        Urgency = (Time Since Last Scrape) * (Base Priority) * (Live Multiplier)
        """
        time_delta = current_time - self.last_scraped_at
        if self.last_scraped_at == 0:
            return float('inf')  # Never scraped? Top priority.
        
        return time_delta * self.base_priority * self.current_multiplier

    def __lt__(self, other):
        # We want a Max-Heap based on urgency, but Python has Min-Heap.
        # So we will implement 'less than' as 'greater urgency' for sorting if we were just sorting list,
        # OR we store negative urgency in the heap. 
        # For simplicity in custom heap implementation, let's just stick to extracting max manually or sorting.
        # Actually simplest is just to recalculate all urgencies and pick max. 
        # Unless we have thousands of terms, O(N) is fine per tick.
        return False # Not used for logic, just structural

class SmartOrchestrator:
    def __init__(self):
        self.terms = []
        self._initialize_buckets()
        print(f"[SCHEDULER] Initialized with {len(self.terms)} terms across buckets.")

    def _initialize_buckets(self):
        """Loads buckets from config and creates SearchTerm objects."""
        if not hasattr(config, 'KEYWORD_BUCKETS'):
            print("[WARN] No KEYWORD_BUCKETS in config. Using fallback.")
            self.terms.append(SearchTerm(config.DEFAULT_SEARCH_QUERY, "Default", 1))
            return

        for bucket_name, data in config.KEYWORD_BUCKETS.items():
            priority = data.get("priority", 1)
            for term in data.get("terms", []):
                self.terms.append(SearchTerm(term, bucket_name, priority))

    def get_next_target(self):
        """Selects the term with the highest urgency score."""
        current_time = time.time()
        best_term = None
        max_urgency = -1.0

        for term_obj in self.terms:
            urgency = term_obj.calculate_urgency(current_time)
            if urgency > max_urgency:
                max_urgency = urgency
                best_term = term_obj
        
        return best_term

    def feedback(self, term_str, new_items_count):
        """
        Adjusts the multiplier based on results found.
        - High result count -> Spike -> Increase freq (Multiplier up)
        - Low result count -> Cooling -> Decrease freq (Multiplier down)
        """
        # Find the term object
        target_obj = next((t for t in self.terms if t.term == term_str), None)
        if not target_obj:
            return

        # Update last scraped time
        target_obj.last_scraped_at = time.time()

        # Dynamic Logic
        if new_items_count >= config.VELOCITY_ALERT_THRESHOLD: # e.g. >= 10
            # Spike detected!
            target_obj.current_multiplier *= 1.5
            # Cap it reasonable
            target_obj.current_multiplier = min(target_obj.current_multiplier, 5.0)
            print(f"[SCHEDULER] ⚠ SPIKE for '{term_str}' (+{new_items_count}). Priority boosted to {target_obj.current_multiplier:.2f}x")
        
        elif new_items_count == 0:
            # Nothing found, cool down slightly
            target_obj.current_multiplier *= 0.9
            target_obj.current_multiplier = max(target_obj.current_multiplier, 0.5) # Don't go below 0.5x
        
        else:
            # Normal maintenance, slowly drift to 1.0
            if target_obj.current_multiplier > 1.0:
                target_obj.current_multiplier *= 0.95
            elif target_obj.current_multiplier < 1.0:
                target_obj.current_multiplier *= 1.05
