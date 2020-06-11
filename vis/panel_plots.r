###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population, 
               total_cost, total_revenue, phones_on_network)

data <- data[(data$confidence == 50),]

data$combined <- paste(data$country, data$scenario, sep="_")

data$scenario = factor(data$scenario, levels=c("low_2_2_2",
                                               "baseline_2_2_2",
                                               "high_2_2_2"),
                                      labels=c("Low (2 Mbps)",
                                               "Baseline (2 Mbps)",
                                               "High (2 Mbps)"))

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

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_revenue, phones_on_network)
data1 <- data1[(data1$strategy == "4G_epc_microwave_baseline_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_cost, phones_on_network)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)
remove(data1, data2)

data$strategy = factor(data$strategy, levels=c(
                            "Revenue",
                            "3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                            "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",  
                            "4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                            "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"
                              ),
                     labels=c("Revenue",
                              "3G (MW)",
                              "3G (FB)",
                              "4G (MW)",
                              "4G (FB)"
                              ))

data$per_user_value <- data$value / data$phones_on_network

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

technology_results <- select(data, combined, strategy, confidence, value, phones_on_network, per_user_value)
  
data <- data %>%
  group_by(combined, country, scenario, strategy) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) +
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") + 
  labs(title = "Cumulative Revenue and Cost by Technology for each Population Decile", colour=NULL,
       subtitle = "Reported for the percentage of population covered with 2 Mbps", 
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") +
  
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) +
  scale_y_continuous(expand = c(0, 0)) + 
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=5)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'technology_cumulative_cost_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
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

################## BUSINESS MODELS 
#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_business_model_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data$scenario = factor(data$scenario, levels=c("low_2_2_2",
                                               "baseline_2_2_2",
                                               "high_2_2_2"),
                       labels=c("Low (2 Mbps)",
                                "Baseline (2 Mbps)",
                                "High (2 Mbps)"))

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

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "4G_epc_microwave_baseline_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_cost)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)
remove(data1, data2)

data <- data[!(data$value == "NA"),]

data$strategy = factor(data$strategy, levels=c("Revenue",
                                              "4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                                               "4G_epc_microwave_pss_baseline_baseline_baseline_baseline",
                                               "4G_epc_microwave_psb_baseline_baseline_baseline_baseline",
                                              "4G_epc_microwave_moran_baseline_baseline_baseline_baseline",
                                              "4G_epc_microwave_cns_baseline_baseline_baseline_baseline",
                                              "4G_epc_microwave_baseline_srn_baseline_baseline_baseline"
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
  theme(axis.text.x = element_text(angle = 45, hjust = 1),legend.position = "bottom") + 
  labs(title = "Impact of Infrastructure Sharing by Decile and Country", colour=NULL,
       subtitle = "Results reported for 4G using microwave backhaul for 2 Mbps per user",
       x = 'Population Covered (%)', y = "Cumulative Cost (Billions $USD)") + 
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'results_business_model_options_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
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

###################NATIONAL COST PROFILE FOR BASELINE
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_cost_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$confidence == 50),]
data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data <- select(data, strategy, combined, ran, backhaul_fronthaul,
               civils, core_network, admin_and_ops, acquisition_per_subscriber, spectrum_cost, 
               tax, profit_margin, used_cross_subsidy, required_state_subsidy)

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

data$strategy = factor(data$strategy, levels=c(
  "3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
  "3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),
  labels=c("3G (MW)",
           "3G (FB)",
           "4G (MW)",
           "4G (FB)"))

data <- gather(data, metric, value, ran:required_state_subsidy)

data$metric = factor(data$metric, levels=c("required_state_subsidy",
                                           "used_cross_subsidy",
                                           "profit_margin",
                                           "tax",
                                           "spectrum_cost",
                                           "admin_and_ops",
                                           "acquisition_per_subscriber",
                                           "ran",
                                           'backhaul_fronthaul',
                                           'civils',
                                           'core_network'
),
labels=c("Required Subsidy",
         "Cross-Subsidy",
         "Profit",
         "Tax",
         "Spectrum",
         "Admin & Ops",
         "Customer Acquisition",
         "RAN",
         "FH/BH",
         "Sites",
         'Core/Regional Fiber'
))

panel <- ggplot(data, aes(x=strategy, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "Aggregate Cost Composition by Strategy and Country", colour=NULL,
       subtitle = "Illustrates required state subsidy under baseline conditions",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=6, reverse = TRUE)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'cost_composition_baseline_national.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

###################DECILE COST PROFILE FOR BASELINE
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_cost_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$confidence == 50),]
data <- data[(data$integration == "baseline"),]
data <- data[(data$scenario == "baseline_2_2_2"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$strategy, sep="_")

data <- select(data, combined, decile, ran, backhaul_fronthaul,
               civils, core_network, admin_and_ops, acquisition_per_subscriber, 
               spectrum_cost, tax, profit_margin,
               used_cross_subsidy, required_state_subsidy)

data$combined = factor(data$combined, 
                       levels=c(
                         "CIV_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "CIV_3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "CIV_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "CIV_4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "KEN_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "KEN_3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "KEN_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "KEN_4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "MLI_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "MLI_3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "MLI_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "MLI_4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "SEN_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "SEN_3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "SEN_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "SEN_4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "TZA_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "TZA_3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "TZA_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "TZA_4G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "UGA_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "UGA_3G_epc_microwave_baseline_baseline_baseline_baseline_baseline",
                         "UGA_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",    
                         "UGA_4G_epc_microwave_baseline_baseline_baseline_baseline_baseline"
                       ),
                       labels=c("Cote D'Ivoire 3G (FB)",
                                "Cote D'Ivoire 3G (MW)",
                                "Cote D'Ivoire 4G (FB)",
                                "Cote D'Ivoire 4G (MW)",
                                "Mali 3G (FB)",
                                "Mali 3G (MW)",
                                "Mali 4G (FB)",
                                "Mali 4G (MW)",
                                "Senegal 3G (FB)",
                                "Senegal 3G (MW)",
                                "Senegal 4G (FB)",
                                "Senegal 4G (MW)",
                                "Kenya 3G (FB)",
                                "Kenya 3G (MW)",
                                "Kenya 4G (FB)",
                                "Kenya 4G (MW)",
                                "Tanzania 3G (FB)",
                                "Tanzania 3G (MW)",
                                "Tanzania 4G (FB)",
                                "Tanzania 4G (MW)",
                                "Uganda 3G (FB)",
                                "Uganda 3G (MW)",
                                "Uganda 4G (FB)",
                                "Uganda 4G (MW)"))

data <- gather(data, metric, value, ran:required_state_subsidy)

data$metric = factor(data$metric, levels=c("required_state_subsidy",
                                           "used_cross_subsidy",
                                           "profit_margin",
                                           "tax",
                                           "spectrum_cost",
                                           "admin_and_ops",
                                           "acquisition_per_subscriber",
                                           "ran",
                                           'backhaul_fronthaul',
                                           'civils',
                                           'core_network'
),
labels=c("Required Subsidy",
         "Cross-Subsidy",
         "Profit",
         "Tax",
         "Spectrum",
         "Admin & Ops",
         "Customer Acquisition",
         "RAN",
         "FH/BH",
         "Sites",
         'Core/Regional Fiber'
))

panel <- ggplot(data, aes(x=decile, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "Decile Cost Composition by Strategy and Country", colour=NULL,
       subtitle = "Illustrates required state subsidy under baseline conditions",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=6, reverse = TRUE)) +
  facet_wrap(~combined, scales = "free", ncol=4)

path = file.path(folder, 'figures', 'cost_composition_baseline_decile.png')
ggsave(path, units="in", width=10, height=10, dpi=300)
print(panel)
dev.off()

################## INTEGRATION RESULTS
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_integration_options.csv'))

data <- data[!(data$total_cost == "NA"),]
# data <- data[(data$scenario == "baseline_2_2_2"),]

names(data)[names(data) == 'GID_0'] <- 'country'

sum_of_costs <- select(data, country, strategy, integration, total_cost)
sum_of_costs <- sum_of_costs %>%
  group_by(country, strategy, integration) %>%
  summarize(total_cost_m = round(sum(total_cost) / 1e6, 3))

data$combined <- paste(data$country, data$strategy, sep="_")

data <- select(data, combined, integration, decile, total_cost)

data$combined = factor(data$combined, 
                       levels=c(
                         "CIV_3G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                        "CIV_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "CIV_4G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "CIV_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "KEN_3G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "KEN_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "KEN_4G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "KEN_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "MLI_3G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "MLI_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "MLI_4G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "MLI_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "SEN_3G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "SEN_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "SEN_4G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "SEN_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "TZA_3G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "TZA_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "TZA_4G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "TZA_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "UGA_3G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "UGA_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",    
                        "UGA_4G_epc_microwave_baseline_baseline_baseline_baseline_integration",
                         "UGA_4G_epc_fiber_baseline_baseline_baseline_baseline_integration"    
                       ),
                       labels=c("Cote D'Ivoire 3G (MW)",
                                "Cote D'Ivoire 3G (FB)",
                                "Cote D'Ivoire 4G (MW)",
                                "Cote D'Ivoire 4G (FB)",
                                "Mali 3G (MW)",
                                "Mali 3G (FB)",
                                "Mali 4G (MW)",
                                "Mali 4G (FB)",
                                "Senegal 3G (MW)",
                                "Senegal 3G (FB)",
                                "Senegal 4G (MW)",
                                "Senegal 4G (FB)",
                                "Kenya 3G (MW)",
                                "Kenya 3G (FB)",
                                "Kenya 4G (MW)",
                                "Kenya 4G (FB)",
                                "Tanzania 3G (MW)",
                                "Tanzania 3G (FB)",
                                "Tanzania 4G (MW)",
                                "Tanzania 4G (FB)",
                                "Uganda 3G (MW)",
                                "Uganda 3G (FB)",
                                "Uganda 4G (MW)",
                                "Uganda 4G (FB)"))

data$integration = factor(data$integration, levels=c("baseline",
                                               "integration"),
labels=c("Baseline",
         "Regional Integration"
))

data <- data[order(data$combined, data$decile, data$integration),]

data <- data %>%
  group_by(combined, decile, integration) %>%
  mutate(cumulative_value_bn = cumsum(round(total_cost / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=integration, group=integration)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),legend.position = "bottom") + 
  labs(title = "Impact of Regional Market Integration by Decile and Country", colour=NULL,
       subtitle = "Results reported for all technologies",
       x = 'Population Covered (%)', y = "Cumulative Cost (Billions $USD)") + 
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=2)) +
  facet_wrap(~combined, scales = "free", ncol=4) 

path = file.path(folder, 'figures', 'results_regional_integration_options_wrap.png')
ggsave(path, units="in", width=10, height=10, dpi=300)
print(panel)
dev.off()

savings <- spread(sum_of_costs, key = integration, value = total_cost_m)
savings$saving_usd <- savings$baseline - savings$integration
savings$saving_perc <- (savings$saving_usd / savings$baseline) * 100

path = file.path(folder, '..', 'results', 'integration_savings.csv')
write.csv(savings, path)

business_model_results <- savings %>% 
  group_by(strategy) %>% 
  summarise(
    raw_min_m = round(min(saving_usd)),
    raw_mean_m = round(mean(saving_usd)), 
    raw_max_m = round(max(saving_usd)),
    perc_min_m = round(min(saving_perc)),
    perc_mean_m = round(mean(saving_perc)), 
    perc_max_m = round(max(saving_perc)),
  )

