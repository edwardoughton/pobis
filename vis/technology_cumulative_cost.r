library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

############################################################
#load data
filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', filename))

data <- data[grep("10_10_10", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, social_cost)

data$scenario = factor(data$scenario, levels=c("low_10_10_10",
                                               "baseline_10_10_10",
                                               "high_10_10_10"),
                       labels=c("Low",
                                "Baseline",
                                "High"))

data$country = factor(data$country, levels=c("CIV",
                                             'MLI',
                                             "SEN",
                                             "KEN",
                                             "TZA",
                                             "UGA"),
                      labels=c("Cote D'Ivoire",
                               "Mali",
                               "Senegal",
                               "Kenya",
                               "Tanzania",
                               "Uganda"
                      ))

data$strategy = factor(data$strategy, levels=c(
  "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
  labels=c("3G (W)",
           "3G (FB)",
           "4G (W)",
           "4G (FB)"))

min_value = round(min(data$social_cost)/1e9,0)
max_value = round(max(data$social_cost)/1e9,0)

social_cost_10mbps = ggplot(data, aes(x=strategy, y=round(social_cost/1e9), 
                               group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(social_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(A) Total Social Cost of Universal Broadband (10 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Social Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)


############################################################
#load data
filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', filename))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, social_cost)

data$scenario = factor(data$scenario, levels=c("low_2_2_2",
                                               "baseline_2_2_2",
                                               "high_2_2_2"),
                       labels=c("Low",
                                "Baseline",
                                "High"))

data$country = factor(data$country, levels=c("CIV",
                                             'MLI',
                                             "SEN",
                                             "KEN",
                                             "TZA",
                                             "UGA"),
                      labels=c("Cote D'Ivoire",
                               "Mali",
                               "Senegal",
                               "Kenya",
                               "Tanzania",
                               "Uganda"
                      ))

data$strategy = factor(data$strategy, levels=c(
  "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
  labels=c("3G (W)",
           "3G (FB)",
           "4G (W)",
           "4G (FB)"))

min_value = round(min(data$social_cost)/1e9,0)
max_value = round(max(data$social_cost)/1e9,0)

social_cost_2mbps = ggplot(data, aes(x=strategy, y=round(social_cost/1e9), 
                               group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(social_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(B) Total Social Cost of Universal Broadband (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Social Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(social_cost_10mbps, social_cost_2mbps,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'social_cost_by_technology.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

###################Cost to Government
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

data <- data[grep("10_10_10", data$scenario), ]
data <- data[!(data$government_cost == "NA"),]
data <- data[(data$confidence == 50),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data$combined <- paste(data$country, data$scenario, sep="_")

data <- select(data, country, scenario, strategy, government_cost)

data$scenario = factor(data$scenario, levels=c("low_10_10_10",
                                               "baseline_10_10_10",
                                               "high_10_10_10"),
                       labels=c("Low",
                                "Baseline",
                                "High"))

data$country = factor(data$country, levels=c("CIV",
                                             'MLI',
                                             "SEN",
                                             "KEN",
                                             "TZA",
                                             "UGA"),
                      labels=c("Cote D'Ivoire",
                               "Mali",
                               "Senegal",
                               "Kenya",
                               "Tanzania",
                               "Uganda"
                      ))

data$strategy = factor(data$strategy, levels=c(
  "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
  labels=c("3G (W)",
           "3G (FB)",
           "4G (W)",
           "4G (FB)"))

min_value = round(min(data$government_cost)/1e9,2)
max_value = round(max(data$government_cost)/1e9, 2)

govt_costs_10mbps = ggplot(data, aes(x=strategy, y=round(government_cost/1e9,1), 
                              group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(government_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(A) Net Government Cost for Universal Broadband (10 Mbps Per User)", 
       colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), 
                     limits = c(min_value-.5, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

###################Cost to Government
#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$government_cost == "NA"),]
data <- data[(data$confidence == 50),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, government_cost)

data$scenario = factor(data$scenario, levels=c("low_2_2_2",
                                               "baseline_2_2_2",
                                               "high_2_2_2"),
                       labels=c("Low",
                                "Baseline",
                                "High"))

data$country = factor(data$country, levels=c("CIV",
                                             'MLI',
                                             "SEN",
                                             "KEN",
                                             "TZA",
                                             "UGA"),
                      labels=c("Cote D'Ivoire",
                               "Mali",
                               "Senegal",
                               "Kenya",
                               "Tanzania",
                               "Uganda"
                      ))

data$strategy = factor(data$strategy, levels=c(
  "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
  labels=c("3G (W)",
           "3G (FB)",
           "4G (W)",
           "4G (FB)"))

min_value = round(min(data$government_cost)/1e9,2)
max_value = round(max(data$government_cost)/1e9, 2)

govt_costs_2mbps = ggplot(data, aes(x=strategy, y=round(government_cost/1e9,1), 
                              group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(government_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(B) Net Government Cost for Universal Broadband (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), 
                     limits = c(min_value-.5, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(govt_costs_10mbps, govt_costs_2mbps,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'govt_cost_by_technology.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()
