// Copyright Chun Shen @ 2016
#ifndef SRC_particleSamples_h_
#define SRC_particleSamples_h_

#include <fstream>
#include <vector>

#include "zlib.h"

#include "./ParameterReader.h"
#include "./particle_info.h"
#include "./particle_decay.h"

using namespace std;

class particleSamples {
 private:
    ParameterReader *paraRdr;
    //! path for results folder
    string path;
    ifstream inputfile;
    ifstream inputfile_mixed_event;
    gzFile inputfile_gz;
    gzFile inputfile_mixed_event_gz;
    int event_buffer_size;

    int echo_level;
    int read_in_mode;
    int run_mode;

    //! the monte-carlo number of the particle of interest
    int particle_monval;

    //! perform resonance feed down for all unstable particles
    int resonance_feed_down_flag;
    //! perform resonance decays for only selected particle species
    int select_resonances_flag;
    //! store the monval of the selected resonance states
    vector<int> select_resonances_list;

    //! include Sigma0 feed down of Lambda
    int resonance_weak_feed_down_flag;

    //! reconst phi meson from (K^+, K^-) pairs
    int reconst_flag;

    //! flag to collect net particle distribution (for run_mode == 2)
    int net_particle_flag;

    //! flag to distinguish particle's isospin
    int flag_isospin;

    //! flag to collect positive and negative charged hadron seperately
    int flag_charge_dependence;

    //! flag to reject from decay particles in the sample
    int reject_decay_flag;
    double tau_reject;

    int particle_urqmd_id, particle_urqmd_isospin;

    int charged_hadron_pdg_list[6];
    int charged_hadron_urqmd_id_list[5];
    int baryon_urqmd_id_list[5];

    //! particle list to store the select particle sample
    vector< vector<particle_info>* >* particle_list;

    //! particle list to store anti-particles
    //! (used when net_particle_flag == 1)
    vector< vector<particle_info>* >* anti_particle_list;

    //! particle list to store the selected particle sample from a mix event
    //! (used when run_mode == 1 for HBT calculation)
    vector< vector<particle_info>* >* particle_list_mixed_event;

    //! particle list to store the resonance particles (Sigma0)
    //! (used when resonance_weak_feed_down_flag == 1)
    vector< vector<particle_info>* >* resonance_list;

    //! particle list to store the (K^+ and K^-) pairs
    //! (used when reconst_flag == 1)
    vector< vector<particle_info>* >* reconst_list_1;
    vector< vector<particle_info>* >* reconst_list_2;
    
    //! particle list to store the positive hadrons
    //! (used when flag_charge_dependence == 1)
    vector< vector<particle_info>* >* positive_charge_hadron_list;
    //! particle list to store the negative hadrons
    //! (used when flag_charge_dependence == 1)
    vector< vector<particle_info>* >* negative_charge_hadron_list;

    //! particle decay
    particle_decay *decayer_ptr;
 public:
    particleSamples(ParameterReader* paraRdr_in, string path_in);
    ~particleSamples();

    void initialize_charged_hadron_urqmd_id_list();
    void initialize_charged_hadron_pdg_list();
    void initialize_baryon_urqmd_id_list();
    void initialize_selected_resonance_list();

    void get_UrQMD_id(int monval);
    int decide_to_pick_UrQMD(int pid, int iso3, int charge,
                             int parent_proc_type);
    int decide_to_pick_UrQMD_resonance(int pid, int iso3, int charge);
    void decide_to_pick_UrQMD_reconst(
                int pid, int iso3, int charge, int parent_proc_type,
                int *flag1, int *flag2);
    int decide_to_pick_JAM(int pid, int *charge_flag);
    int decide_to_pick_UrQMD_anti_particles(int pid, int iso3,
                                            int charge);
    int decide_to_pick_from_OSCAR_file(int monval);
    int decide_to_pick_OSCAR(int monval);

    int get_pdg_id(int urqmd_id, int urqmd_isospin);

    void perform_resonance_feed_down(
                vector< vector<particle_info>* >* input_particle_list);
    void perform_weak_resonance_feed_down();
    void perform_particle_reconstruction(); 

    int read_in_particle_samples();
    int read_in_particle_samples_mixed_event();
    int read_in_particle_samples_OSCAR();
    int read_in_particle_samples_OSCAR_mixed_event();
    int read_in_particle_samples_JAM();
    int read_in_particle_samples_JAM_mixed_event();
    int read_in_particle_samples_UrQMD();
    int read_in_particle_samples_UrQMD_mixed_event();
    int read_in_particle_samples_UrQMD_zipped();
    int read_in_particle_samples_UrQMD_mixed_event_zipped();
    int read_in_particle_samples_UrQMD_3p3();
    int read_in_particle_samples_UrQMD_3p3_mixed_event();
    int read_in_particle_samples_Sangwook();
    int read_in_particle_samples_mixed_event_Sangwook();

    string gz_readline(gzFile gzfp);
    bool end_of_file() {
        if (read_in_mode == 2) {
            return(gzeof(inputfile_gz));
        } else {
            return(inputfile.eof());
        }
    }
    bool end_of_file_mixed_event() {
        if (read_in_mode == 2) {
            return(gzeof(inputfile_mixed_event_gz));
        } else {
            return(inputfile_mixed_event.eof());
        }
    }

    int get_event_buffer_size() {return(event_buffer_size);}

    int get_number_of_events() {return(particle_list->size());}
    int get_number_of_events_anti_particle() {
        return(anti_particle_list->size());
    }
    int get_number_of_mixed_events() {
        return(particle_list_mixed_event->size());
    }

    int get_number_of_particles(int event_id) {
        return((*particle_list)[event_id]->size());
    }
    int get_number_of_particles_mixed_event(int event_id) {
        return((*particle_list_mixed_event)[event_id]->size());
    }
    int get_number_of_anti_particles(int event_id) {
        return((*anti_particle_list)[event_id]->size());
    }
    int get_number_of_positive_particles(int event_id) {
        return((*positive_charge_hadron_list)[event_id]->size());
    }
    int get_number_of_negative_particles(int event_id) {
        return((*negative_charge_hadron_list)[event_id]->size());
    }

    particle_info get_particle(int event_id, int part_id) {
        return((*(*particle_list)[event_id])[part_id]);
    }
    particle_info get_anti_particle(int event_id, int part_id) {
        return((*(*anti_particle_list)[event_id])[part_id]);
    }
    particle_info get_particle_from_mixed_event(int event_id, int part_id) {
        return((*(*particle_list_mixed_event)[event_id])[part_id]);
    }
    particle_info get_positive_particle(int event_id, int part_id) {
        return((*(*positive_charge_hadron_list)[event_id])[part_id]);
    }
    particle_info get_negative_particle(int event_id, int part_id) {
        return((*(*negative_charge_hadron_list)[event_id])[part_id]);
    }
};

#endif  // SRC_particleSamples_h_
