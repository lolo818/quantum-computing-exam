import neal
from ttictoc import tic, toc


def local(model, num_reads, num_sweeps):
    bqm = model.to_bqm()
    sa = neal.SimulatedAnnealingSampler()

    tic()
    sampleset = sa.sample(bqm, num_reads=num_reads, num_sweeps=num_sweeps)
    run_time = toc()

    # Decode solution
    decoded_samples = model.decode_sampleset(sampleset)
    best_sample = min(decoded_samples, key=lambda x: x.energy)
    

    return {
        "solve": best_sample.sample,  # 最佳解
        "run_time": run_time,  # 執行時間
        "broken_constrs": best_sample.constraints(only_broken=True),
    }
