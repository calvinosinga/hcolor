import h5py as hp
import numpy as np
from colossus.cosmology import cosmology
from scipy.ndimage import gaussian_filter
INFILE = '/scratch/zt1/project/diemer-prj/user/cosinga/hcolor/output/fiducial_tng300B_%03dS_0A_800R/grids/vncombine2_tng300B_%03dS_0A_800R.hdf5'

snaps = [50, 67]

grid_name = 'CICW_vn_redshift_mass_mass_vn'

out_file = '/scratch/zt1/project/diemer-prj/user/cosinga/hcolor/output/beam_pk.hdf5'

w = hp.File(out_file, 'w')
for s in snaps:
    f = hp.File(INFILE%(s, s), 'r')
    print(list(f.keys()), grid_name)
    og_grid = f[grid_name][:]
    for beam in ['mkt', 'gbt']:
        grid = np.copy(og_grid)
        npts = grid.shape[0]
        box_length = 205 # Mpc/h from TNG website
        if s == 67:
            redshift = 0.5
        elif s == 50:
            redshift = 1
        
        nu_21cm = 1420.405751#MHz
        c = 299792458 # speed of light m/s
        nu = nu_21cm / (1+redshift) # effective frequency of observations
        # Calculate beam size:
        if beam == 'gbt':
            D_dish = 100 # diameter of telescope dish in metres
            
        elif beam == 'mkt':

            D_dish = 13.5
        theta_FWHM = np.degrees(c / (nu*1e6 * D_dish)) # freq-dependent beam size
        sig_FWHM = theta_FWHM/(2*np.sqrt(2*np.log(2)))

        # set cosmo
        cosmo = cosmology.setCosmology('planck15') # using TNG's cosmology
        d_c = cosmo.comovingDistance(redshift) # already in Mpc/h

        R_beam = d_c * np.radians(sig_FWHM)
        dpix = box_length / npts
        R_beam_pix = R_beam / dpix
        for i in range(npts):
            grid[:, :, i] = gaussian_filter(grid[:, :, i], sigma = R_beam_pix, mode = 'wrap')
        
        w.create_dataset('%s_%03d_beam'%(beam, s), data = grid)

    f.close()
w.close()
