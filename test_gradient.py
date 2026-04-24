import datetime as dt

class MockSlot:
    def __init__(self, start_time, end_time, coverage):
        self.start_time = start_time
        self.end_time = end_time
        self.coverage = coverage

def build_gradient(start_time, end_time, slots):
    start_m = start_time.hour * 60 + start_time.minute
    end_m = end_time.hour * 60 + end_time.minute
    total_duration = max(1, end_m - start_m)
    
    stops = []
    for slot in slots:
        slot_start_m = slot.start_time.hour * 60 + slot.start_time.minute
        slot_end_m = slot.end_time.hour * 60 + slot.end_time.minute
        
        start_pct = max(0, (slot_start_m - start_m) / total_duration * 100)
        end_pct = min(100, (slot_end_m - start_m) / total_duration * 100)
        
        if slot.coverage == "covered":
            color = "#e0f2e7"
        elif slot.coverage == "cancelled":
            color = "#f9e2e0"
        else:
            color = "#fff9c4"
            
        stops.append(f"{color} {start_pct:.1f}%")
        stops.append(f"{color} {end_pct:.1f}%")
        
    return f"background: linear-gradient(to bottom, {', '.join(stops)});"

slots = [
    MockSlot(dt.time(18, 0), dt.time(19, 0), "covered"),
    MockSlot(dt.time(19, 0), dt.time(20, 0), "uncovered")
]
print(build_gradient(dt.time(18, 0), dt.time(20, 0), slots))
