###plot pysim5g lookup tables
# install.packages("tidyverse")
library(tidyverse)
library(plyr)
library(ggpubr)
#####################

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#get path to full tables via the data folder
full_tables <- file.path(folder, '..', 'data', 'raw', 'pysim5g', 'full_tables')

#get a list of all files in the folder ending in .csv
myfiles = list.files(path=full_tables, pattern="*.csv", full.names=TRUE)

#import data for all files in file list
data = ldply(myfiles, read_csv)

# lut = file.path(folder, '..', 'data', 'raw', 'pysim5g', 'capacity_lut_by_frequency.csv')
# data = read.csv(lut)

data = data[data$transmittion_type == '1x1' |
            data$transmittion_type == '2x2'
            ,]

data = data[data$frequency_GHz == 2.1 |
            data$frequency_GHz == 0.8 |
              data$frequency_GHz == 0.7 |
              data$frequency_GHz == 1.8
,]

# data <- data[!(data$generation == "5G"),]

# #drop results over 5km distance
# data = data[data$inter_site_distance_m <= 10000,]
#drop results over 5km distance
data = data[data$r_distance <= 7500,]

#turn env into factor and relabel
data$environment = factor(data$environment, levels=c("urban",
                                                     "suburban",
                                                     "rural"),
                          labels=c("Urban",
                                   "Suburban",
                                   "Rural"))

data$combined <- paste(data$generation, data$frequency_GHz, sep="_")

data$combined = factor(data$combined,
                          levels=c("3G_1.8",
                                   "3G_2.1",
                                   "4G_0.7",
                                   "4G_0.8",
                                   "4G_1.8",
                                   "4G_2.1"),
                          labels=c("1.8 (3G)",
                                   "2.1 (3G)",
                                   "0.7 (4G)",
                                   "0.8 (4G)",
                                   "1.8 (4G)",
                                   "2.1 (4G)"))
unique(data$combined)
#subset the data for plotting
data = select(data, inter_site_distance_m, r_distance, environment,
              combined, spectral_efficiency_bps_hz, capacity_mbps)

se = ggplot(data, aes(x=r_distance/1000, y=spectral_efficiency_bps_hz,
                        colour=factor(combined))) +
  # geom_point(size=0.1) +
  geom_smooth(size=0.5) +
  scale_x_continuous(expand = c(0, 0), limits=c(0,7.5)) +
  scale_y_continuous(expand = c(0, 0), limits=c(0,10.5)) +
  theme(legend.position="bottom") + guides(colour=guide_legend(ncol=7)) +
  labs(title = 'Mean Spectral Efficiency by Frequency and Technology',
       x = 'Cell Radius (km)', y='Spectral Efficiency (Bps/Hz)',
       colour='Frequency (GHz)') +
  facet_wrap(~environment)

path = file.path(folder, 'figures', 'se_panel.png')
ggsave(path, units="in", width=7, height=3.5)
print(se)
dev.off()
