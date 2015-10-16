def intro():
    """Displays introduction to the program."""

    print "An Interactive Analytic QG Model for Synoptic Meteorology"
    print u"         Copyright \u00a9 2014 Steven G. Decker"
    print
    print "You are viewing a Python implementation of the analytic QG model"
    print "presented by Frederick Sanders in the May 1971 issue of"
    print "Monthly Weather Review."
    print
    print "Use the checkboxes to turn on/off various fields.  Note that vectors"
    print "may end up underneath filled contours depending on the order with"
    print "which you click things.  A restart will fix this."
    print
    print "A number of model parameters may be changed with the sliders:"
    print "p      - Which isobaric surface to view [hPa]"
    print "L      - Wavelength [km] (i.e., distance between T/Z maxima)"
    print u"\u03bb/L    - Phase shift between T and \u03a6 perturbations"
    print "a      - Temperature gradient of background [K/km]"
    print "p_trop - Tropopause pressure [hPa]"
    print "T_hat  - Temperature perturbation magnitude [K]"
    print u"\u03a6\u2080_hat - Geopotential perturbation magnitude [J/kg]"