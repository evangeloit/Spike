#pragma once

#include "Spike/RecordingElectrodes/CollectNeuronSpikesRecordingElectrodes.hpp"
#include "RecordingElectrodes.hpp"
#include "Spike/Backend/CUDA/CUDABackend.hpp"
#include <cuda.h>
#include <vector_types.h>
#include <curand.h>
#include <curand_kernel.h>

namespace Backend {
  namespace CUDA {
    class CollectNeuronSpikesRecordingElectrodes :
      public virtual ::Backend::CUDA::RecordingElectrodesCommon,
      public ::Backend::CollectNeuronSpikesRecordingElectrodes {
    public:
      MAKE_BACKEND_CONSTRUCTOR(CollectNeuronSpikesRecordingElectrodes);
      // ~CollectNeuronSpikesRecordingElectrodes();

      virtual void reset_state();
      virtual void prepare();

      virtual void copy_spikes_to_front(::CollectNeuronSpikesRecordingElectrodes* front);
      virtual void copy_spike_counts_to_front(::CollectNeuronSpikesRecordingElectrodes* front);

      virtual void collect_spikes_for_timestep(::CollectNeuronSpikesRecordingElectrodes* front,
                                               float current_time_in_seconds);


      int* neuron_ids_of_stored_spikes_on_device = nullptr;
      int* total_number_of_spikes_stored_on_device = nullptr;
      float* time_in_seconds_of_stored_spikes_on_device = nullptr;
    };

    __global__ void collect_spikes_for_timestep_kernel
    (float* d_last_spike_time_of_each_neuron,
     int* d_total_number_of_spikes_stored_on_device,
     int* d_neuron_ids_of_stored_spikes_on_device,
     float* d_time_in_seconds_of_stored_spikes_on_device,
     float current_time_in_seconds,
     size_t total_number_of_neurons);
  }
}