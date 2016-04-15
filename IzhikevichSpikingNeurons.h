#ifndef IzhikevichSpikingNeurons_H
#define IzhikevichSpikingNeurons_H

//	CUDA library
#include <cuda.h>

#include "SpikingNeurons.h"

struct izhikevich_neuron_struct : public neuron_struct {
	izhikevich_neuron_struct(): test(0.0f) { neuron_struct(); }   // default Constructor

	float test;
};

class IzhikevichSpikingNeurons : public SpikingNeurons {
public:
	// Constructor/Destructor
	IzhikevichSpikingNeurons();
	~IzhikevichSpikingNeurons();

	float * param_a;
	float * param_b;

	float * d_param_a;
	float * d_param_b;

	virtual int AddGroupNew(neuron_struct *params, int shape[2]);
	virtual void initialise_device_pointersNew();
	virtual void reset_neuron_variables_and_spikesNew();

	void izhikevich_state_update_wrapper(float* current_injection, float timestep);

};

#endif