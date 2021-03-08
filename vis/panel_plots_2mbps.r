###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

###########################################################
####Technology costs
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_market_results_technology_options.csv'))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population,
               total_market_cost, total_market_revenue, total_phones)

data <- data[(data$confidence == 50),]

data$combined <- paste(data$country, data$scenario, sep="_")

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
                                    labels=c("Cote D'Ivoire (ECOWAS)",
                                             "Mali (ECOWAS)",
                                             "Senegal (ECOWAS)",
                                             "Kenya (EAC)",
                                             "Tanzania (EAC)",
                                             "Uganda (EAC)"
                                             ))

data$combined = factor(data$combined,
       levels=c("CIV_low_2_2_2", "CIV_baseline_2_2_2", "CIV_high_2_2_2",
                "MLI_low_2_2_2", "MLI_baseline_2_2_2", "MLI_high_2_2_2",
                "SEN_low_2_2_2", "SEN_baseline_2_2_2", "SEN_high_2_2_2",
                "KEN_low_2_2_2", "KEN_baseline_2_2_2", "KEN_high_2_2_2",
                "TZA_low_2_2_2", "TZA_baseline_2_2_2", "TZA_high_2_2_2",
                "UGA_low_2_2_2", "UGA_baseline_2_2_2", "UGA_high_2_2_2"),
       labels=c("Cote D'Ivoire (Low)","Cote D'Ivoire (Baseline)","Cote D'Ivoire (High)",
                "Mali (2 Mbps) (Low)", "Mali (2 Mbps) (Baseline)", "Mali (2 Mbps) (High)",
                "Senegal (2 Mbps) (Low)", "Senegal (2 Mbps) (Baseline)", "Senegal (2 Mbps) (High)",
                "Kenya (2 Mbps) (Low)", "Kenya (2 Mbps) (Baseline)", "Kenya (2 Mbps) (High)",
                "Tanzania (2 Mbps) (Low)", "Tanzania (2 Mbps) (Baseline)", "Tanzania (2 Mbps) (High)",
                "Uganda (2 Mbps) (Low)", "Uganda (2 Mbps) (Baseline)", "Uganda (2 Mbps) (High)"
                ))

perc_tech_cost_saving = data 

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_market_revenue, total_phones)
data1 <- data1[(data1$strategy == "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_market_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_market_cost, total_phones)
names(data2)[names(data2) == 'total_market_cost'] <- 'value'
data <- rbind(data1, data2)
remove(data1, data2)

data$strategy = factor(data$strategy, levels=c(
                            "Revenue",
                            "3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
                            "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
                            "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
                            "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"
                              ),
                     labels=c("Revenue",
                              "3G (W)",
                              "3G (FB)",
                              "4G (W)",
                              "4G (FB)"
                              ))

data$per_user_value <- data$value / data$total_phones

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

technology_results <- select(data, combined, strategy, confidence, value, total_phones, per_user_value)

data <- data %>%
  group_by(combined, country, scenario, strategy) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, group=strategy)) +
  geom_line(aes(linetype=strategy, colour=strategy, size=strategy)) +
  scale_linetype_manual(values=c(1,2,3,4,5,6)) +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  scale_size_manual(values=c(.5,.5,.5,.5,.5))+
  theme(axis.text.x = element_text(angle = 0, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Private Cost for Broadband Universal Service", 
       colour=NULL, linetype=NULL, size=NULL,
       subtitle = "Reported by population coverage for 2 Mbps broadband universal service",
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") +
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) +
  scale_y_continuous(expand = c(0, 0)) +
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=5), linetype=guide_legend(ncol=5)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'b_technology_cumulative_cost_wrap_2mbps.png')
ggsave(path, units="in", width=7, height=8.5, dpi=300)
print(panel)
dev.off()

technology_results <- technology_results %>%
  group_by(combined, strategy, confidence) %>%
  summarise(
    value_m = round(sum(value)/1e6),
    phones_on_network_m = round(sum(total_phones)/1e6),
    per_user_value = round(mean(per_user_value))
    ) %>%
  group_by(strategy, confidence) %>%
  summarise(
    value_min_m = round(min(value_m)),
    value_mean_m = round(mean(value_m)),
    value_max_m = round(max(value_m)),
      )

remove(panel)

perc_tech_cost_saving = select(perc_tech_cost_saving, country, scenario, 
                               strategy, confidence,total_market_cost)

baseline = perc_tech_cost_saving[(
  data$strategy == '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline' 
),]
baseline = select(baseline, country, scenario, confidence, total_market_cost)
names(baseline)[names(baseline) == 'total_market_cost'] <- 'baseline'

perc_tech_cost_saving = merge(perc_tech_cost_saving, baseline, 
             by=c('country', 'scenario', 'confidence'),
             all.x=TRUE)

perc_tech_cost_saving$saving = round(
          (perc_tech_cost_saving$total_market_cost - 
             perc_tech_cost_saving$baseline) / 
            perc_tech_cost_saving$total_market_cost * 100)

perc_tech_cost_saving = perc_tech_cost_saving %>%
  group_by(scenario, strategy, confidence) %>%
  summarize(
    saving = round(mean(saving)),
  )

###################Social cost
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

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

social_cost = ggplot(data, aes(x=strategy, y=round(social_cost/1e9), 
                               group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(social_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(A) Total Social Cost of Broadband Universal Service (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Social Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)


###################Cost to Government
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$government_cost == "NA"),]
data <- data[(data$confidence == 50),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data$combined <- paste(data$country, data$scenario, sep="_")

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

govt_costs = ggplot(data, aes(x=strategy, y=round(government_cost/1e9,1), 
                              group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(government_cost/1e9,1)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(B) Net Government Cost for Broadband Universal Service (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(min_value-.5, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(social_cost, govt_costs,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'd_social_and_govt_cost_2mbps.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

remove(data)

###################Social cost 2 Mbps
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

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

social_cost = ggplot(data, aes(x=strategy, y=round(social_cost/1e9), 
                               group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(social_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(A) Total Social Cost of Broadband Universal Service (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Social Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

###################Cost to Government
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$government_cost == "NA"),]
data <- data[(data$confidence == 50),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data$combined <- paste(data$country, data$scenario, sep="_")

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

govt_costs = ggplot(data, aes(x=strategy, y=round(government_cost/1e9,1), 
                              group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(government_cost/1e9,1)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(B) Net Government Cost for Broadband Universal Service (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(min_value-.5, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(social_cost, govt_costs,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'd_social_and_govt_cost_2mbps.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

remove(data)

