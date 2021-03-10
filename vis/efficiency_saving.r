###################Efficiency factor
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

data <- data[grep("10_10_10", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, required_efficiency_saving)

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

data$required_efficiency_saving[data$required_efficiency_saving < 0] <- 0

min_value = round(min(data$required_efficiency_saving),0)
max_value = round(max(data$required_efficiency_saving),0)

efficiency_saving_10mbps = ggplot(data, 
                           aes(x=strategy, y=round(required_efficiency_saving), 
                               group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(required_efficiency_saving,0)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) +
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(A) Regional Efficiency Saving Required for Viability (10 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = " Required Percentage Saving (%) to Achieve Viability") +
  scale_y_continuous(expand = c(0, 0), limits = c(min_value-.5, max_value+9),
                     breaks = seq(0, 100, by = 20)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

###############################################################################
#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, required_efficiency_saving)

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

data$required_efficiency_saving[data$required_efficiency_saving < 0] <- 0

min_value = round(min(data$required_efficiency_saving),0)
max_value = round(max(data$required_efficiency_saving),0)

efficiency_saving_2mbps = ggplot(data, 
                                  aes(x=strategy, y=round(required_efficiency_saving), 
                                      group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(required_efficiency_saving,0)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) +
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "(B) Regional Efficiency Saving Required for Viability (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = " Required Percentage Saving (%) to Achieve Viability") +
  scale_y_continuous(expand = c(0, 0), limits = c(min_value-.5, max_value+9),
                     breaks = seq(0, 100, by = 20)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)


combined <- ggarrange(efficiency_saving_10mbps, efficiency_saving_2mbps,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'efficiency_saving.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

remove(data)
