###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, '..', 'results')

filename = 'per_user_cost_by_pop_density_2.csv'
data1 <- read.csv(file.path(folder_inputs, filename))
data1$Capacity = '(2 Mbps)'

filename = 'per_user_cost_by_pop_density_10.csv'
data2 <- read.csv(file.path(folder_inputs, filename))
data2$Capacity = '(10 Mbps)'

data = rbind(data1, data2)

remove(data1, data2)

data <- data[(data$Confidence == 50),]

data$combined <- paste(data$Scenario, data$Capacity, sep=" ")

data$combined = factor(data$combined, levels=c("High (10 Mbps)",
                                               "High (2 Mbps)",
                                               "Baseline (10 Mbps)",
                                               "Baseline (2 Mbps)",
                                               "Low (10 Mbps)",
                                               "Low (2 Mbps)"
                                               ))
data$Strategy = factor(data$Strategy, levels=c("4G (W)",
                                               "4G (FB)",
                                               "3G (W)",
                                               "3G (FB)"))
data$Decile = factor(data$Decile, levels=c("<20",
                                               "20-43",
                                               "43-69",
                                               "69-109",
                                               "109-171",
                                               "171-257",
                                               "257-367",
                                               "367-541",
                                               "541-1104",
                                               ">1104"
                                               ),
                     labels=c("<20",
                              "<43",
                              "<69",
                              "<109",
                              "<171",
                              "<257",
                              "<367",
                              "<541",
                              "<1104",
                              ">1104"
                     ))

data <- select(data, combined, Strategy, Decile, 
               private_median_cpu,
               govt_median_cpu, 
               social_median_cpu
)

totals <- data %>%
  group_by(combined, Strategy, Decile) %>%
  summarize(social_cost = round(
    (private_median_cpu + govt_median_cpu)/1000,1))

colnames(data)[colnames(data) == 'private_median_cpu'] <- 'Private Cost ($USD)'
colnames(data)[colnames(data) == 'govt_median_cpu'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'social_median_cpu'] <- 'social_cost'

data <- data %>% gather(key="Cost_Type", value="value",
                        'Private Cost ($USD)', 
                        'Government Cost ($USD)', 
)

min_value = min(round(data$social_cost/1000,1))
max_value = max(round(data$social_cost/1000,1))

data$value = round(data$value/1000,1)

ggplot(data, aes(y=value, x=Decile, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(Decile, social_cost, label=social_cost, fill=NULL),
            size = 2.2, data = totals, vjust=-.4) +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  labs(title = "Social Cost Per User by Population Density for Universal Broadband", 
       colour=NULL,
       subtitle="Reported by strategy, scenario adoption and capacity per user",
       x=expression ("Population Density"~(km^2) ), 
       y="Social Cost (1000s $USD) (Median)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-min_value, max_value+2)) + 
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(combined~Strategy)

path = file.path(folder, 'figures', 'social_cost_per_user_by_pop_density.png')
ggsave(path, units="in", width=8, height=9.5, dpi=300)
dev.off()
