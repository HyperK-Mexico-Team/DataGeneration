import argparse
import subprocess
import random
import math
import os


class sWCSimGenerateData(object):

    def __init__(self):
        # Set parameters to choose.
        #
        parser = argparse.ArgumentParser(description="Generate several .root files of data for "
                                                     "different particles, energy, directions and initial positions "
                                                     "of the WCSim")
        group = parser.add_argument_group()
        group.add_argument("-l", "--levels", dest="levels", type=int, default=1,
                           help="Number of different levels of energy to simulate. "
                                "If levels=1, only needed the min energy.")
        group.add_argument("-b", "--batch", dest="batch", type=int, default=1,
                           help="Batch of simulations with the same level of energy.")
        group.add_argument("-v", "--events", dest="events", type=int, default=10,
                           help="Number of events per simulation.")
        group.add_argument("-g", "--geometry", dest="geometry", type=str,
                           choices=['SuperK', 'SuperK_20inchPMT_20perCent ',
                                    'SuperK_20inchBandL_20perCent', 'nuPRISM',
                                    'SuperK_12inchBandL_15perCent ',
                                    'SuperK_20inchBandL_14perCent',
                                    'HyperK',
                                    'HyperKWithOD',
                                    'HyperK_20perCent',
                                    'Cylinder_60x74_20inchBandL_14perCent',
                                    'Cylinder_60x74_20inchBandL_40perCent',
                                    'Cylinder_12inchHPD_15perCent',
                                    'EggShapedHyperK',
                                    'EggShapedHyperK_withHPD'], default='SuperK',
                           help="Set geometry of the tank, default geometry: SuperK.")
        group.add_argument("-q", "--particle", dest="particle", type=str, default="e-",
                           choices=["e-", "pi0", "mu-", "gamma"],
                           help="Particle to shoot from  G4 Particle Gun.")
        group.add_argument("-i", "--min_energy", dest="min_energy", type=float, default=100.0,
                           help="Set MIN energy of the range of simulations, in MeV")
        group.add_argument("-a", "--max_energy", dest="max_energy", type=float, default=1000.0,
                           help="Set MAX energy of the range of simulations, in MeV")
        parser.add_argument("-o", type=str, dest="output_file", default=None,
                            help="Output file name. Default: results/wcsim_output_<particle>_<energy>_<gen_id>.root")
        parser.add_argument("-d", "--direction", dest="direction",
                            type=float, nargs=3, help="Initial direction of particle. Default: 1,0,0")
        parser.add_argument("-p", "--position", dest="position",
                            type=float, nargs=3, help="Initial position of particle. Default: 0,0,0")
        parser.add_argument("-rd", "--random_direction", dest="random_direction", action="store_true",
                            help="Generates random initial directions for particle.")
        parser.add_argument("-rp", "--random_position", dest="random_position", action="store_true",
                            help="Generates random initial direction for particle.")
        parser.add_argument("-sd", "--swept_direction", dest="swept_direction", action="store_true",
                            help="Generates simulations in disctints angles ( in order ) in the plane xy.")
        self._args = parser.parse_args()

    def get_str_energy(self, x):
        if x < 0.001:
            return "{} eV".format(x * 1000000)
        if x < 1:
            return "{} keV".format(x * 1000)
        if x < 1000:
            return "{} MeV".format(x)
        if x < 1000000:
            return "{} GeV".format(x / 1000.0)
        else:
            return "{} TeV".format(x / 1000000.0)

    def generate_macro(self, particle, energy, events, direction, position, output_dir_name,
                       output_file_name, geometry=None):
        with open("WCSim.mac", "w") as macro:
            macro.write("# Sample setup macro with no visualization. Generated with python3 script.\n")
            macro.write("/run/verbose 1\n")
            macro.write("/tracking/verbose 0\n")
            macro.write("/hits/verbose 0\n\n")
            macro.write("## select the geometry\n")
            macro.write("# Default config if you do nothing is currently SuperK\n\n")
            if geometry:
                geometry_config = "/WCSim/WCgeom " + geometry + "\n"
                macro.write(geometry_config)
            else:
                macro.write("/WCSim/WCgeom SuperK \n")
            macro.write("# Select which PMT to use: \n")
            macro.write("# /WCSim/nuPRISM/SetPMTType PMT8inch \n")
            macro.write("# /WCSim/nuPRISM/SetPMTPercentCoverage 40 \n")
            macro.write("# Set height of nuPRISM inner detector \n")
            macro.write("# /WCSim/nuPRISM/SetDetectorHeight 6. m \n")
            macro.write("# Set vertical position of inner detector, in beam coordinates\n")
            macro.write("# /WCSim/nuPRISM/SetDetectorVerticalPosition 0. m\n")
            macro.write("# Set diameter of inner detector\n")
            macro.write("# /WCSim/nuPRISM/SetDetectorDiameter 8. m\n")

            macro.write("\n# Set Gadolinium doping (concentration is in percent)\n")
            macro.write("# /WCSim/DopingConcentration 0.1\n")
            macro.write("# /WCSim/DopedWater false\n")
            macro.write("# /WCSim/Construct\n")

            macro.write("\n# Use mPMTs settings (uncomment/delete the above)\n")
            macro.write("# /WCSim/WCgeom nuPRISM_mPMT\n")
            macro.write("# /WCSim/WCgeom nuPRISMShort_mPMT\n")
            macro.write("# Set Gadolinium doping (concentration is in percent)\n")
            macro.write("# /WCSim/DopingConcentration 0.1\n")
            macro.write("# /WCSim/DopedWater false\n")
            macro.write("#/WCSim/Construct\n")
            macro.write("## OR for single mPMT mode or updating mPMT parameters:\n")
            macro.write("#/control/execute macros/mPMT_nuPrism1.mac\n")
            macro.write("## mPMT options: mPMT_nuPrism1.mac and 2.mac\n")

            macro.write("\n# Added for the PMT QE option 08/17/10 (XQ)\n")
            macro.write("# 1. Stacking only mean when the photon is generated\n")
            macro.write("# the QE is applied to reduce the total number of photons\n")
            macro.write("# 2. Stacking and sensitivity detector\n")
            macro.write("# In the stacking part, the maximum QE is applied to reduce\n")
            macro.write("# the total number of photons\n")
            macro.write("# On the detector side, the rest of QE are applied according to QE/QE_max\n")
            macro.write("# distribution. This option is in particular important for the WLS\n")
            macro.write("# 3. The third option means all the QE are applied at the detector\n")
            macro.write("# Good for the low energy running.\n")
            macro.write("# 4. Switch off the QE, ie. set it at 100%\n")
            macro.write("/WCSim/PMTQEMethod     Stacking_Only\n")
            macro.write("#/WCSim/PMTQEMethod     Stacking_And_SensitiveDetector\n")

            macro.write("#/WCSim/PMTQEMethod     SensitiveDetector_Only\n")
            macro.write("#/WCSim/PMTQEMethod     DoNotApplyQE\n")

            macro.write("#turn on or off the collection efficiency\n")
            macro.write("/WCSim/PMTCollEff on\n")

            macro.write("# command to choose save or not save the pi0 info 07/03/10 (XQ)\n")
            macro.write("/WCSim/SavePi0 false\n")

            macro.write("#choose the Trigger & Digitizer type (and options)\n")
            macro.write("/DAQ/Digitizer SKI\n")
            macro.write("/DAQ/Trigger NDigits\n")

            macro.write("#grab the other DAQ options (thresholds, timing windows, etc.)\n")
            macro.write("/control/execute macros/daq.mac\n")

            macro.write(
                "\n# default dark noise frequency (and conversion factor) is PMT property (NEW), set in the code.\n")
            macro.write("# Below gives possibility to overwrite nominal values, eg. to switch OFF the Dark Noise.\n")
            macro.write("# /DarkRate/SetDarkRate 0 kHz   #Turn dark noise off\n")
            macro.write("/DarkRate/SetDarkRate 4.2 kHz  # This is the value for SKI set in SKDETSIM.\n")
            macro.write("# /DarkRate/SetDarkRate 8.4 kHz #For 20 inch HPDs and Box and Line PMTs,"
                        " based on High QE 20in R3600 dark rate from EGADS nov 2014\n")
            macro.write("# /DarkRate/SetDarkRate 3.0 kHz #For 12 inch HPDs and Box and Line PMTs,"
                        " based on High QE 20in R3600 dark rate from EGADS nov 2014\n")

            macro.write("\n# command to multiply the dark rate.\n")
            macro.write("# Convert dark noise frequency before digitization "
                        "to after digitization by setting suitable factor\n")
            macro.write("# Again, this is now a PMT property and can be overridden here\n")
            macro.write("/DarkRate/SetConvert 1.367  # For Normal PMT\n")
            macro.write("# /DarkRate/SetConvert 1.119 #For HPDs\n")
            macro.write("# /DarkRate/SetConvert 1.126 #For Box and Line PMTs\n")

            macro.write("\n# Select which time window(s) to add dark noise to\n")
            macro.write("# /DarkRate/SetDarkMode 0 to add dark noise to a time window starting at\n")
            macro.write("# /DarkRate/SetDarkLow to /DarkRate/SetDarkHigh [time in ns]\n")
            macro.write("# /DarkRate/SetDarkMode 1 adds dark noise hits to a window of\n")
            macro.write("# width /DarkRate/SetDarkWindow [time in ns] around each hit\n")
            macro.write("# i.e. hit time ± (/DarkRate/SetDarkWindow) / 2\n")
            macro.write("/DarkRate/SetDarkMode 1\n")
            macro.write("/DarkRate/SetDarkHigh 100000\n")
            macro.write("/DarkRate/SetDarkLow 0\n")
            macro.write("/DarkRate/SetDarkWindow 4000\n")
            macro.write("# Uncomment one of the lines below if you want to use the OGLSX or RayTracer visualizer\n")
            macro.write("# /control/execute macros/visOGLSX.mac\n")
            macro.write("# /control/execute macros/visRayTracer.mac\n")
            macro.write("# /control/execute macros/visOGLQT.mac             ## NEW\n")

            macro.write("## select the input nuance-formatted vector file\n")
            macro.write("## you can of course use your own\n")
            macro.write("# /mygen/generator muline\n")
            macro.write("# /mygen/vecfile inputvectorfile\n")
            macro.write("# /mygen/vecfile h2o.2km.001-009x3_G4.kin\n")
            macro.write("# /mygen/vecfile mu+.out\n")

            macro.write("\n# Or you can use the G4 Particle Gun\n")
            macro.write("# for a full list of /gun/ commands see:\n")
            macro.write("# http://geant4.web.cern.ch/geant4/G4UsersDocuments/"
                        "UsersGuides/ForApplicationDeveloper/html/Control/UIcommands/_gun_.html\n")
            macro.write("/mygen/generator gun\n")
            macro.write(f"/gun/particle {particle}\n")
            macro.write(f"/gun/energy {energy}\n")
            macro.write(f"/gun/direction {direction[0]} {direction[1]} {direction[2]}\n")
            macro.write(f"/gun/position {position[0]} {position[1]} {position[2]}\n")
            macro.write("\n# Or you can use the G4 General Particle Source\n")
            macro.write(
                "# you can do a lot more with this than a monoenergetic, monodirectional, single-particle gun\n")
            macro.write("# for a full list of /gps/ commands see:\n")
            macro.write("# https://geant4.web.cern.ch/geant4/UserDocumentation/UsersGuides"
                        "/ForApplicationDeveloper/html/ch02s07.html\n")
            macro.write("# /mygen/generator gps\n")
            macro.write("# /gps/particle e-\n")
            macro.write("# /gps/energy 500 MeV\n")
            macro.write("# /gps/direction 1 0 0\n")
            macro.write("# /gps/position 0 0 0\n")

            macro.write("\n# Or you can use the laser option\n")
            macro.write("# This is equivalent to the gps command, except that the "
                        "gps particle energies are saved ignoring their mass\n")
            macro.write("# for a full list of /gps/ commands see:\n")
            macro.write("# https://geant4.web.cern.ch/geant4/UserDocumentation/UsersGuides"
                        "/ForApplicationDeveloper/html/ch02s07.html\n")
            macro.write("# It is used for laser calibration simulation\n")
            macro.write("# /mygen/generator laser\n")
            macro.write("# /gps/particle opticalphoton\n")
            macro.write("# /gps/energy 2.505 eV\n")
            macro.write("# /gps/direction 1 0 0\n")
            macro.write("# /gps/position 0 0 0\n")
            macro.write("# /gps/number 1000\n")
            macro.write("# /gps/ang/type iso\n")
            macro.write("# /gps/ang/mintheta 0 deg\n")
            macro.write("# /gps/ang/maxtheta 30 deg\n")
            macro.write("# /gps/ang/minphi 0 deg\n")
            macro.write("# /gps/ang/maxphi 360 deg\n")

            macro.write("\n##### NEW\n")
            macro.write("/Tracking/fractionOpticalPhotonsToDraw 0.0\n")

            macro.write(f"\n## change the name of the output root file, default = wcsim_output_<energy>"
                        "_<particle>_<gen_id>.root\n")
            macro.write(f"/WCSimIO/RootFile {output_dir_name}/{output_file_name}\n")

            macro.write("\n## Boolean to select whether to save the NEUT "
                        "RooTracker vertices in the output file, provided "
                        "you used\n")
            macro.write("## a NEUT vector file as input\n")
            macro.write("/WCSimIO/SaveRooTracker 0\n")

            macro.write("\n## set a timer running on WCSimRunAction\n")
            macro.write("# /WCSimIO/Timer false\n")
            macro.write(f"/run/beamOn {events}\n")
            macro.write("#exit\n")

    def execute(self):
        path = os.path.dirname(os.path.abspath(__file__))
        output_dir_name = "results"
        os.makedirs(os.path.join(path, output_dir_name), exist_ok=True)

        if self._args.direction:
            direction = self._args.direction
        else:
            direction = [1, 0, 0]

        if self._args.position:
            position = self._args.position
        else:
            position = [0, 0, 0]

        for levels in range(self._args.levels):
            energyInMeV = (levels / self._args.levels) * (self._args.max_energy - self._args.min_energy) + \
                          self._args.min_energy
            strEnergy = self.get_str_energy(energyInMeV)

            # Generates a random offset ( starting angle ) for the swept
            if self._args.swept_direction:
                angle_offset = random.random() * 2 * math.pi
            for batch in range(self._args.batch):
                gen_id = str(batch) if batch >= 10 else "0{0}".format(batch)

                if self._args.random_direction:
                    x = random.random()
                    y = random.random()
                    z = (1 - x * x + y * y) ** .5
                    direction = [x, y, z]
                elif self._args.swept_direction:
                    angle = 2 * math.pi * (batch / self._args.batch) + angle_offset
                    x, y, z = math.cos(angle), math.sin(angle), 0
                    direction = [x, y, z]
                output_name_file = self._args.output_file
                if not output_name_file:
                    energ = strEnergy.replace(" ", "_")
                    output_name_file = f"wcsim_output_{self._args.particle}_{energ}_{gen_id}.root"

                print("id:", gen_id, "number of events:", self._args.events,
                      "particle:", self._args.particle, "energy:", strEnergy, "direction:", direction,
                      "position:", position, "geometry:", self._args.geometry, "output file:", output_name_file)
                self.generate_macro(self._args.particle, strEnergy, self._args.events, direction, position,
                                    output_dir_name, output_name_file, geometry=self._args.geometry)
                subprocess.run(["./WCSim", "WCSim.mac"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    _script = sWCSimGenerateData()
    _script.execute()

