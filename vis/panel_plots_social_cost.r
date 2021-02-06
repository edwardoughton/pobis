###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

####Technology costs
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_mno_cost_results_technology_options.csv'))

data <- data[!(data$total_mno_cost == "NA"),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population,
               social_cost, total_mno_revenue, phones_on_network)

data <- data[(data$confidence == 50),]

data$combined <- paste(data$country, data$scenario, sep="_")

data$scenario = factor(data$scenario, levels=c("low_10_10_10",
                                               "baseline_10_10_10",
                                               "high_10_10_10"),
                       labels=c("Low (10 Mbps)",
                                "Baseline (10 Mbps)",
                                "High (10 Mbps)"))

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
                       levels=c("CIV_low_10_10_10", "CIV_baseline_10_10_10", "CIV_high_10_10_10",
                                "MLI_low_10_10_10", "MLI_baseline_10_10_10", "MLI_high_10_10_10",
                                "SEN_low_10_10_10", "SEN_baseline_10_10_10", "SEN_high_10_10_10",
                                "KEN_low_10_10_10", "KEN_baseline_10_10_10", "KEN_high_10_10_10",
                                "TZA_low_10_10_10", "TZA_baseline_10_10_10", "TZA_high_10_10_10",
                                "UGA_low_10_10_10", "UGA_baseline_10_10_10", "UGA_high_10_10_10"),
                       labels=c("Cote D'Ivoire (Low)","Cote D'Ivoire (Baseline)","Cote D'Ivoire (High)",
                                "Mali (10 Mbps) (Low)", "Mali (10 Mbps) (Baseline)", "Mali (10 Mbps) (High)",
                                "Senegal (10 Mbps) (Low)", "Senegal (10 Mbps) (Baseline)", "Senegal (10 Mbps) (High)",
                                "Kenya (10 Mbps) (Low)", "Kenya (10 Mbps) (Baseline)", "Kenya (10 Mbps) (High)",
                                "Tanzania (10 Mbps) (Low)", "Tanzania (10 Mbps) (Baseline)", "Tanzania (10 Mbps) (High)",
                                "Uganda (10 Mbps) (Low)", "Uganda (10 Mbps) (Baseline)", "Uganda (10 Mbps) (High)"
                       ))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_mno_revenue, phones_on_network)
data1 <- data1[(data1$strategy == "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_mno_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, social_cost, phones_on_network)
names(data2)[names(data2) == 'social_cost'] <- 'value'
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

data$per_user_value <- data$value / data$phones_on_network

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

technology_results <- select(data, combined, strategy, confidence, value, 
                             phones_on_network, per_user_value)

data <- data %>%
  group_by(combined, country, scenario, strategy) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) +
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 0, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Social Cost by Technology", colour=NULL,
       subtitle = "Reported by population coverage for 10 Mbps broadband universal service",
       x="Population Covered (%)", y="Cumulative Social Cost (Billions $USD)") +
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) +
  scale_y_continuous(expand = c(0, 0)) +
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=5)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'b_technology_cumulative_social_cost_wrap.png')
ggsave(path, units="in", width=7, height=8.5, dpi=300)
print(panel)
dev.off()

technology_results <- technology_results %>%
  group_by(combined, strategy, confidence) %>%
  summarise(
    value_m = round(sum(value)/1e6),
    phones_on_network_m = round(sum(phones_on_network)/1e6),
    per_user_value = round(mean(per_user_value))
  ) %>%
  group_by(strategy, confidence) %>%
  summarise(
    value_min_m = round(min(value_m)),
    value_mean_m = round(mean(value_m)),
    value_max_m = round(max(value_m)),
  )

###################NATIONAL COST PROFILE FOR BASELINE
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_mno_cost_results_technology_options.csv'))

data <- data[!(data$total_mno_cost == "NA"),]
data <- data[(data$confidence == 50),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data <- select(data, strategy, combined, ran, backhaul_fronthaul,
               civils, core_network, administration, spectrum_cost,
               tax, profit_margin, used_cross_subsidy, required_state_subsidy)

data$combined = factor(data$combined,
                       levels=c("CIV_low_10_10_10", "CIV_baseline_10_10_10", "CIV_high_10_10_10",
                                "MLI_low_10_10_10", "MLI_baseline_10_10_10", "MLI_high_10_10_10",
                                "SEN_low_10_10_10", "SEN_baseline_10_10_10", "SEN_high_10_10_10",
                                "KEN_low_10_10_10", "KEN_baseline_10_10_10", "KEN_high_10_10_10",
                                "TZA_low_10_10_10", "TZA_baseline_10_10_10", "TZA_high_10_10_10",
                                "UGA_low_10_10_10", "UGA_baseline_10_10_10", "UGA_high_10_10_10"),
                       labels=c("Cote D'Ivoire (Low)","Cote D'Ivoire (Baseline)","Cote D'Ivoire (High)",
                                "Mali (10 Mbps) (Low)", "Mali (10 Mbps) (Baseline)", "Mali (10 Mbps) (High)",
                                "Senegal (10 Mbps) (Low)", "Senegal (10 Mbps) (Baseline)", "Senegal (10 Mbps) (High)",
                                "Kenya (10 Mbps) (Low)", "Kenya (10 Mbps) (Baseline)", "Kenya (10 Mbps) (High)",
                                "Tanzania (10 Mbps) (Low)", "Tanzania (10 Mbps) (Baseline)", "Tanzania (10 Mbps) (High)",
                                "Uganda (10 Mbps) (Low)", "Uganda (10 Mbps) (Baseline)", "Uganda (10 Mbps) (High)"
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

data <- gather(data, metric, value, ran:required_state_subsidy)

data$metric = factor(data$metric, levels=c("required_state_subsidy",
                                           "used_cross_subsidy",
                                           "profit_margin",
                                           "tax",
                                           "spectrum_cost",
                                           "administration",
                                           'core_network',
                                           'civils',
                                           'backhaul_fronthaul',
                                           "ran"
),
labels=c("Required State Subsidy",
         "User Cross-Subsidy",
         "Profit",
         "Tax",
         "Spectrum",
         "Administration",
         'Core',
         "Civils",
         "Backhaul",
         "RAN"
))

panel <- ggplot(data, aes(x=strategy, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "Broadband Universal Service Cost Composition", colour=NULL,
       subtitle = "Reported for all cost types under baseline conditions",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=6, reverse = TRUE)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'c_cost_composition_baseline_national.png')
ggsave(path, units="in", width=7, height=8.5, dpi=300)
print(panel)
dev.off()


################## BUSINESS MODELS
#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_mno_results_business_model_options.csv'))

data <- data[!(data$total_mno_cost == "NA"),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data$scenario = factor(data$scenario, levels=c("low_10_10_10",
                                               "baseline_10_10_10",
                                               "high_10_10_10"),
                       labels=c("Low (10 Mbps)",
                                "Baseline (10 Mbps)",
                                "High (10 Mbps)"))

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
                       levels=c("CIV_low_10_10_10", "CIV_baseline_10_10_10", "CIV_high_10_10_10",
                                "MLI_low_10_10_10", "MLI_baseline_10_10_10", "MLI_high_10_10_10",
                                "SEN_low_10_10_10", "SEN_baseline_10_10_10", "SEN_high_10_10_10",
                                "KEN_low_10_10_10", "KEN_baseline_10_10_10", "KEN_high_10_10_10",
                                "TZA_low_10_10_10", "TZA_baseline_10_10_10", "TZA_high_10_10_10",
                                "UGA_low_10_10_10", "UGA_baseline_10_10_10", "UGA_high_10_10_10"),
                       labels=c("Cote D'Ivoire (Low)","Cote D'Ivoire (Baseline)","Cote D'Ivoire (High)",
                                "Mali (10 Mbps) (Low)", "Mali (10 Mbps) (Baseline)", "Mali (10 Mbps) (High)",
                                "Senegal (10 Mbps) (Low)", "Senegal (10 Mbps) (Baseline)", "Senegal (10 Mbps) (High)",
                                "Kenya (10 Mbps) (Low)", "Kenya (10 Mbps) (Baseline)", "Kenya (10 Mbps) (High)",
                                "Tanzania (10 Mbps) (Low)", "Tanzania (10 Mbps) (Baseline)", "Tanzania (10 Mbps) (High)",
                                "Uganda (10 Mbps) (Low)", "Uganda (10 Mbps) (Baseline)", "Uganda (10 Mbps) (High)"
                       ))

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_mno_revenue)
data1 <- data1[(data1$strategy == "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_mno_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_mno_cost)
names(data2)[names(data2) == 'total_mno_cost'] <- 'value'
data <- rbind(data1, data2)
remove(data1, data2)

data <- data[!(data$value == "NA"),]

data$strategy = factor(data$strategy, levels=c("Revenue",
                                               "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
                                               "4G_epc_wireless_pss_baseline_baseline_baseline_baseline",
                                               "4G_epc_wireless_psb_baseline_baseline_baseline_baseline",
                                               "4G_epc_wireless_moran_baseline_baseline_baseline_baseline",
                                               "4G_epc_wireless_cns_baseline_baseline_baseline_baseline",
                                               "4G_epc_wireless_baseline_srn_baseline_baseline_baseline"
),
labels=c("Revenue",
         "Baseline (No sharing)",
         "Passive Site Sharing",
         "Passive Backhaul Sharing",
         "Active Sharing",
         "Core Network Sharing",
         "Shared Rural Network"
))

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

business_model_results <- select(data, combined, strategy, confidence, value)

data <- data %>%
  group_by(combined, country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) +
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 0, hjust = 1),legend.position = "bottom") +
  labs(title = "Impact of Infrastructure Sharing on Cumulative Cost", colour=NULL,
       subtitle = "Reported using 4G (W) to provide 10 Mbps broadband universal service",
       x = 'Population Covered (%)', y = "Cumulative Cost (Billions $USD)") +
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'd_results_business_model_options_wrap.png')
ggsave(path, units="in", width=7, height=8.5, dpi=300)
print(panel)
dev.off()

business_model_results <- business_model_results %>%
  group_by(combined, strategy, confidence) %>%
  summarise(
    value_m = round(sum(value)/1e6)
  ) %>%
  group_by(strategy, confidence) %>%
  summarise(
    value_min_m = round(min(value_m)),
    value_mean_m = round(mean(value_m)),
    value_max_m = round(max(value_m)),
  )


