# DataGeneration
Scripts for Data generation with WCSim.

## WCSim data generation
This script has the objective of running multiple WCSim simulations for generate batches of data easily.


### Considerations
The file `wcsim_data_generation.py` should be located inside the /WCSim_build folder. 

### Usage
For a Quick Start, just Run `python3 wcsim_data_generation.py
This will generate the following result:

    $ python3 wcs_generate_data.py
    id: 00 , number of events: 10 , particle: e- , energy: 100.0 MeV , direction: [1, 0, 0] , position: [0, 0, 0] , geometry: SuperK , output file: wcsim_output_e-_100.0_MeV_00.root

We already ran WCSim with no need of opening the Geant4 GUI!.
Let's dive into the output.

> We generate  a simulation for 10 events in the SuperK experiemnt, for
> an electron of energy of 100.0 MeV, with certain initial position and
> direction. The output file of the results will be stored into the file
> wcsim_output_e-_100.0_MeV_00.root

With this script we can run multiple events, with multiple energies, directions, positions, for a given particle in certain geometry.

#### Setting Parameters
We can customize our simulations and batches of data adding the following on required arguments:

*Optional arguments:*
- 
| Flag                    | Description                                                                                                 | Args needed   | Default value                                  |
|-------------------------|-------------------------------------------------------------------------------------------------------------|---------------|------------------------------------------------|
| -h --help               | Usage of the script                                                                                         |               | N/A                                            |
| -o                      | Output file ( not recommended to use ).                                                                     | file_name     | wcsim_output_<particle>_<energy>_<gen_id>.root |
| -d --direction          | Initial direction (unitary vector) of the particle inside the tank,  in cartesian coordinates < x, y, z >.  | num num num   | 1  0  0                                        |
|  -p --position          | Initial position ( in mts, center of the tank as origin ) of the particle. <x,y,z>                          | num num num   | 0  0  0                                        |
| -rd  --random_direction | Generates random initial directions for particle.                                                           |               | N/A                                            |
| -rp --random_position   | Generates random initial positions in the tank for the particle.                                            |               | N/A                                            |
| -sd --swept_direction   | Generates simulations in disctints angles ( in order ) into the plane xy.                                   |               | N/A                                            |
| -i --min_energy         | Set MIN energy of the range of simulations, in MeV                                                          | num           | 100  (MeV)                                     |
| -a --max_energy         | Set MAX energy of the range of simulations, in MeV                                                          | num           |                                                |
| -l --levels             | Number of different levels of energy to simulate. If levels=1, only needed the min energy.                  | num           | 1                                              |
| -b --batch              | Batch of simulations with the same level of energy.                                                         | num           | 1                                              |
| -v --events             | Number of events per simulation.                                                                            | num           | 1                                              |
| -g                      | Geometry of the tank. (Read the apendix of valid geometries).                                               | geometry_name | SuperK                                         |
| -q                      | Particle to shoot from G4 Particle Gun. ( e- , pi0 , mu- , gamma )                                          | particle_name | e-                                             |


### Valid Geometries
There are a list of Geometries that could be used. Please select the one needed from this list:

SuperK,SuperK_20inchPMT_20perCent,SuperK_20inchBandL_20perCent,nuPRISM,SuperK_12inchBandL_15perCent,SuperK_20inchBandL_14perCent,HyperK,HyperKWithOD,HyperK_20perCent,Cylinder_60x74_20inchBandL_14perCent,Cylinder_60x74_20inchBandL_40perCent,Cylinder_12inchHPD_15perCent,EggShapedHyperK,EggShapedHyperK_withHPD
