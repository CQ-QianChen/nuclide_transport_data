The data describes the diffusion coefficients of nuclides in pure water at a reference temperature of 25 Celsius degree. The data were compiled from [Li & Gregory (1974)](https://doi.org/10.1016/0016-7037(74)90145-8) and are classified into two groups:

- Low diffusivity group: This includes alkaline earth metals, transition metals, lanthanides, and actinides, which are assigned a reference value of $7.5( \pm 2.5) \times 10^{-10} \mathrm{~m}^2 / \mathrm{s}$

- High diffusivity group: This includes ions like $\mathrm{Cl}^{-}$, $\mathrm{Br}^{-}, \mathrm{I}^{-}, \mathrm{K}^{+}, \mathrm{Cs}^{+}, \mathrm{Ag}^{+}$, and HTO (tritiated water), which are assigned a reference value of $20.0( \pm 2.5) \times 10^{-10} \mathrm{~m}^2 / \mathrm{s}$.

## Structure of the YAML file 
The layout of the YAML files follows a specific structure:

If no value is provided for a specific entry field, then enter null.

```
nuclide:
  source: STR                       # String with BibTeX key of data source.
  type: STR                         # String out of [scalar, dictionary, expression].
  value: VAL                        # A value of type float, integer, string, or dictionary.
  value_min: VAL                    # Minimum value.
  value_max: VAL                    # Maximum value.
  value_std: VAL                    # Standard deviation of the value.
  probability_distribution:
    sample_size: INT                # Number of samples to be drawn.
    sampled_data: LIST[VAL] or STR  # List of sampled data or a scipy.stats.rv_continuous().rvs() function.
  unit_str: STR                     # Standard string to indicate unit.
  unit_base: LIST(INT)              # An array of the form [ kg m s K A mol cd ] that gives the unit as the exponent of the SI basis units, e.g., m/s^2 is [0, 1, -2, 0, 0, 0, 0].
  variable_name: STR                # Function argument (e.g., temperature) (must be used if type is dictionary or expression).
  variable_unit_str: STR            # Standard string to indicate variable_unit.
  variable_unit_base: LIST(INT)     # See above (must be used if type is tabulated or expression).
  description: STR                  # Free text metadata.
  tag:
    agency: LIST[STR]               # List of agencies that provided the data.
    location: LIST[STR]             # List of locations where the data applies.
    simplified_lithology: LIST[STR] # List of simplified lithologies the data applies to.
    ID: STR                         # A generated unique Universally Unique IDentifier (UUID) for the data entry.
``` 
