#!/usr/bin/env python3

import boutvecma
import easyvvuq as uq
import chaospy
import os

campaign = uq.Campaign(name="Conduction")
encoder = boutvecma.BOUTEncoder(template_input="models/conduction/data/BOUT.inp")
decoder = boutvecma.BOUTDecoder(variables=["T"])
params = {
    "conduction:chi": {"type": "float", "min": 0.0, "max": 2.0, "default": 1.0},
    "T:scale": {"type": "float", "min": 0.0, "max": 100.0, "default": 1.0},
}

campaign.add_app("1D_conduction", params=params, encoder=encoder, decoder=decoder)

vary = {
    "conduction:chi": chaospy.Uniform(0.8, 1.2),
    "T:scale": chaospy.Uniform(0.5, 1.5),
}

sampler = uq.sampling.PCESampler(vary=vary, polynomial_order=3)
campaign.set_sampler(sampler)

campaign.draw_samples()

run_dirs = campaign.populate_runs_dir()

print(f"Created run directories: {run_dirs}")

campaign.apply_for_each_run_dir(
    uq.actions.ExecuteLocal(os.path.abspath("build/models/conduction/conduction -d ."))
)

campaign.collate()

campaign.apply_analysis(uq.analysis.PCEAnalysis(sampler=sampler, qoi_cols=["T"]))

results = campaign.get_last_analysis()

results.plot_moments("T")
