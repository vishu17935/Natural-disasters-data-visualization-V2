final_risk_merged.csv

columns

Index(['DisNo.', 'Historic', 'Classification Key', 'Disaster Group',
       'Disaster Subgroup', 'Disaster Type', 'Disaster Subtype',
       'External IDs', 'Event Name', 'ISO', 'Country_x', 'Subregion', 'Region',
       'Location', 'Origin', 'Associated Types', 'OFDA/BHA Response', 'Appeal',
       'Declaration', 'AID Contribution ('000 US$)', 'Magnitude',
       'Magnitude Scale', 'Latitude', 'Longitude', 'River Basin', 'Start Year',
       'Start Month', 'Start Day', 'End Year', 'End Month', 'End Day',
       'Total Deaths', 'No. Injured', 'No. Affected', 'No. Homeless',
       'Total Affected', 'Reconstruction Costs ('000 US$)',
       'Reconstruction Costs, Adjusted ('000 US$)',
       'Insured Damage ('000 US$)', 'Insured Damage, Adjusted ('000 US$)',
       'Total Damage ('000 US$)', 'Total Damage, Adjusted ('000 US$)', 'CPI',
       'Admin Units', 'Entry Date', 'Last Update', 'gdp_per_capita',
       'gdp_per_capita_ppp', 'hospital_beds', 'hdi', 'urban_population_pct',
       'gov_effectiveness', 'population_density', 'Disaster_Score',
       'Average_Risk_Index', 'World Risk Index', 'Exposure', 'Vulnerability',
       'Susceptibility', 'Coping Capacity', 'Adaptive Capacity'],
      dtype='object')

risk_data.csv
columns


Index(['WRI.Country', 'ISO3.Code', 'Year', 'W', 'E', 'V', 'S', 'C', 'A',
       'S_01',
       ...
       'AI_04a_Norm', 'AI_04a_Base', 'AI_04b_Norm', 'AI_04b_Base',
       'AI_04c_Norm', 'AI_04c_Base', 'AI_05a_Norm', 'AI_05a_Base',
       'AI_05b_Norm', 'AI_05b_Base'],
      dtype='object', length=248)


ranked_data.csv : contains ranks of some metrics year wise among the countries that had disasters that year
columns
same as final_risk_merged.csv but with additional columns
'rank_damages', 'rank_risk_y', 'rank_gdp', 'rank_hdi_y',
       'rank_vulnerability'



same as 