###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, '..', 'results')

data1 <- read.csv(file.path(folder_inputs, 'total_cost_estimates_2.csv'))
data1$Capacity = '2 Mbps Per User'

data2 <- read.csv(file.path(folder_inputs, 'total_cost_estimates_10.csv'))
data2$Capacity = '10 Mbps Per User'

data = rbind(data1, data2)

remove(data1, data2)

data <- data[(data$Confidence == 50),]

data <- select(data, Scenario, Strategy, Capacity, 
               Private.Cost...Bn., Government.Cost...Bn.,
               Social.Cost...Bn.)


data$Scenario = factor(data$Scenario, levels=c("Low",
                                               "Baseline",
                                               "High"))

data$Capacity = factor(data$Capacity, levels=c("2 Mbps Per User",
                                               "10 Mbps Per User"
))

totals <- data %>%
  group_by(Scenario, Strategy, Capacity) %>%
  summarize(social_cost = round(
    (Private.Cost...Bn. + Government.Cost...Bn.)/1000, 2))

colnames(data)[colnames(data) == 'Private.Cost...Bn.'] <- 'Private Cost ($USD)'
colnames(data)[colnames(data) == 'Government.Cost...Bn.'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'Social.Cost...Bn.'] <- 'social_cost'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Cost ($USD)', 
                        'Government Cost ($USD)', 
                        )

min_value = min(round(data$social_cost/1e3, 2))
max_value = max(round(data$social_cost/1e3, 2))

data$value = round(data$value/1e3, 2)

ggplot(data, aes(y=value, x=Strategy, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(Strategy, social_cost, label = social_cost, fill = NULL), 
            size = 2.5, data = totals, hjust=-.2) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "Total Social Cost of Universal Broadband Across Africa", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Social Cost (Trillions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-min_value, max_value+0.4)) + 
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
 facet_grid(Capacity~Scenario)

path = file.path(folder, 'figures', 'total_social_cost_across_Africa.png')
ggsave(path, units="in", width=8, height=5, dpi=300)
dev.off()