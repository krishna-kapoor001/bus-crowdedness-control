import math
from backend.app.schemas.schemas import (
    SimulationRequest, SimulationResponse, CorridorImpact, AlternativeWindow
)

class SimulationService:
    def __init__(self):
        self.corridors_base = [
            {"name": "Mehrauli-Badarpur Corridor", "base_daily": 24800, "capacity": 22000},
            {"name": "Ring Road South & Central", "base_daily": 31200, "capacity": 30000},
            {"name": "South-West Kapashera Corridor", "base_daily": 19500, "capacity": 18000},
            {"name": "Trans-Yamuna East Arterial", "base_daily": 21400, "capacity": 20000},
            {"name": "GT Karnal North Corridor", "base_daily": 16800, "capacity": 17500},
            {"name": "Airport Expressway Corridor", "base_daily": 14200, "capacity": 15000},
        ]

    def run_simulation(self, req: SimulationRequest) -> SimulationResponse:
        """
        CrowdShift Simulation Engine:
        Computes counterfactual demand shift across network corridors based on:
        - Overall demand multiplier (req.demand_multiplier, e.g. 1.20 for +20%)
        - Peak hour shift factor (req.peak_shift_factor, e.g. -0.15 for 15% shift to shoulders)
        """
        mult = req.demand_multiplier
        peak_shift = req.peak_shift_factor

        total_orig = sum(c["base_daily"] for c in self.corridors_base)
        corridor_results = []
        total_sim = 0

        for c in self.corridors_base:
            base = c["base_daily"]
            cap = c["capacity"]

            # Mathematical simulation formula:
            # Simulated demand incorporates overall growth and peak elasticity
            # elasticity factor per corridor sensitivity
            elasticity = 1.1 if "Ring Road" in c["name"] or "Mehrauli" in c["name"] else 0.95
            sim_demand = int(base * (mult + (peak_shift * elasticity * 0.4)))
            sim_demand = max(1000, sim_demand)
            total_sim += sim_demand

            delta_pct = round(((sim_demand - base) / base) * 100, 1)

            # Classify original vs simulated crowd level based on volume-to-capacity ratio (V/C)
            orig_vc = base / cap
            sim_vc = sim_demand / cap

            def vc_to_level(vc: float) -> str:
                if vc > 1.15:
                    return "VERY HIGH"
                elif vc > 0.95:
                    return "HIGH"
                elif vc > 0.70:
                    return "MODERATE"
                else:
                    return "LOW"

            orig_lvl = vc_to_level(orig_vc)
            sim_lvl = vc_to_level(sim_vc)

            if delta_pct > 12:
                impact = "SEVERE"
            elif delta_pct > 3:
                impact = "MODERATE"
            elif delta_pct < -5:
                impact = "RELIEVED"
            else:
                impact = "MINIMAL"

            corridor_results.append(CorridorImpact(
                corridor_name=c["name"],
                original_demand=base,
                simulated_demand=sim_demand,
                delta_pct=delta_pct,
                original_crowd_level=orig_lvl,
                simulated_crowd_level=sim_lvl,
                impact_level=impact
            ))

        system_delta = round(((total_sim - total_orig) / total_orig) * 100, 1)

        # Alternative time window recommendations
        recommendations = [
            AlternativeWindow(
                time_slot="06:30 - 07:30 (Early Shoulder)",
                crowd_reduction_pct=round(34.2 - (peak_shift * 10), 1),
                recommended_for="Commuters seeking guaranteed seating before morning peak surge"
            ),
            AlternativeWindow(
                time_slot="10:30 - 11:30 (Post-Morning Shoulder)",
                crowd_reduction_pct=round(41.5 - (peak_shift * 8), 1),
                recommended_for="Flexible work hours and midday travel with 28% lower boarding delay"
            ),
            AlternativeWindow(
                time_slot="15:30 - 16:30 (Pre-Evening Window)",
                crowd_reduction_pct=round(48.0 - (peak_shift * 5), 1),
                recommended_for="Off-peak transit before evening rush-hour bottleneck"
            ),
        ]

        scenario_label = f"Simulated Scenario: {int(mult*100)}% Volume | Peak Shift {int(peak_shift*100)}%"
        rationale = (
            f"Calculated via Volume-to-Capacity (V/C) network elasticity model. "
            f"Simulates {mult:.2f}x passenger demand scaling with a {peak_shift:+.1%} peak dispersal factor. "
            f"Net network effect: {system_delta:+.1f}% shift across 6 major monitored arterial corridors."
        )

        return SimulationResponse(
            scenario_name=scenario_label,
            demand_multiplier=mult,
            peak_shift_factor=peak_shift,
            total_original_demand=total_orig,
            total_simulated_demand=total_sim,
            system_wide_delta_pct=system_delta,
            corridors=corridor_results,
            shift_recommendations=recommendations,
            mathematical_rationale=rationale
        )

simulation_service = SimulationService()
