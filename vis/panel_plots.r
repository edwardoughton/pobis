###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, 'subscriptions', "data_inputs")

files = list.files(path=folder_inputs, pattern="*.csv")

data <- 
  do.call("rbind", 
          lapply(files, 
                 function(x) 
                   read.csv(file.path(folder_inputs, x), 
                            stringsAsFactors = FALSE)))

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

data$scenario = factor(data$scenario, levels=c("low",
                                               'baseline',
                                               "high"
),
labels=c("Low",
         "Baseline",
         "High"
))

data = data[complete.cases(data),]

subscriptions = ggplot(data, aes(x=year, y=penetration, group=country)) +
  geom_point(aes(shape=country, color=country), size=1) +
  geom_line(aes(color=country)) +
  scale_shape_manual(values=c(0, 1, 2, 3, 4, 5)) +
  scale_size_manual(values=c(0.1, 0.1, 0.1, 0.1, 0.1)) + 
  scale_color_manual(values=c("#009E73", "#F0E442","#E69F00", "#56B4E9","#D55E00", "#0072B2")) + 
  geom_vline(xintercept=2020, linetype="dashed", color = "grey", size=.5) +
  scale_x_continuous(expand = c(0, 0.5), limits = c(2010,2030), 
                     breaks = seq(2010,2030,2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), 
        legend.position = "bottom", legend.title=element_blank()) +
  labs(title = "(A) Mobile Subscriptions by Country", 
       x = NULL, y = "Subscribers (%)") +
  guides(shape=guide_legend(ncol=6), colour=guide_legend(ncol=6)) +
  facet_grid(~scenario)

####################smartphones
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'regional_annual_demand_technology_options.csv'))

data <- data[(data$confidence == 50),]
names(data)[names(data) == 'GID_0'] <- 'country'

data = data[(
    data$strategy == '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'
),]

data <- select(data, country, scenario, geotype, year, 
               population, population_with_smartphones)

data$geotype[data$geotype == 'suburban'] <- 'urban'

data = data %>%
  group_by(country, scenario, geotype, year) %>%
  summarize(population = sum(population),
            smartphones = sum(population_with_smartphones))

data$geotype = factor(data$geotype,
                      levels=c("urban",
                               "rural"),
                      labels=c("Urban",
                               "Rural"))

data$scenario = factor(data$scenario,
                      levels=c("low_10_10_10",
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

data$penetration = round(data$smartphones /
                              data$population * 100, 2) 

smartphones = ggplot(data, aes(x=year, y=penetration, group=country)) +
  geom_point(aes(shape=country, color=country), size=1) +
  geom_line(aes(color=country)) +
  scale_shape_manual(values=c(0, 1, 2, 3, 4, 5)) +
  scale_color_manual(values=c("#009E73", "#F0E442","#E69F00", "#56B4E9","#D55E00", "#0072B2")) + 
  scale_x_continuous(expand = c(0, 0.25), limits = c(2020,2030), 
                     breaks = seq(2020,2030,2)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0,67)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), 
        legend.position = "bottom", legend.title=element_blank()) +
  labs(title = "(B) Smartphone Penetration by Country", 
       x = NULL, y = "Smartphones (%)") +
  guides(shape=guide_legend(ncol=6), colour=guide_legend(ncol=6)) +
  # facet_wrap(settlement_type~scenario, ncol=3, scales='free_y')
  facet_grid(geotype~scenario)

combined <- ggarrange(subscriptions, smartphones, 
                      ncol = 1, nrow = 2,
                      common.legend = TRUE, 
                      legend='bottom', heights=c(3.5, 5))

path = file.path(folder, 'figures', 'a_demand_graphic.png')
ggsave(path, units="in", width=7, height=5.5, dpi=300)
print(combined)
dev.off()

remove(subscriptions, smartphones, combined, data)

###########################################################
####Technology costs
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_mno_results_technology_options.csv'))

data <- data[!(data$total_mno_cost == "NA"),]
# data <- data[(data$integration == "baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population,
               total_mno_cost, total_mno_revenue, phones_on_network)

data <- data[(data$confidence == 50),]

data$combined <- paste(data$country, data$scenario, sep="_")

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

perc_tech_cost_saving = data#[(data$scenario == 'baseline_10_10_10'),]

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_mno_revenue, phones_on_network)
data1 <- data1[(data1$strategy == "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_mno_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_mno_cost, phones_on_network)
names(data2)[names(data2) == 'total_mno_cost'] <- 'value'
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

technology_results <- select(data, combined, strategy, confidence, value, phones_on_network, per_user_value)

data <- data %>%
  group_by(combined, country, scenario, strategy) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) +
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 0, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Private Cost for Broadband Universal Service", colour=NULL,
       subtitle = "Reported by population coverage for 10 Mbps broadband universal service",
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") +
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) +
  scale_y_continuous(expand = c(0, 0)) +
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=5)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'b_technology_cumulative_cost_wrap.png')
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

remove(data, panel)


perc_tech_cost_saving = select(perc_tech_cost_saving, country, scenario, strategy, confidence, 
                         total_mno_cost)

baseline = perc_tech_cost_saving[(
  data$strategy == '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline' 
),]
baseline = select(baseline, country, scenario, confidence, total_mno_cost)
names(baseline)[names(baseline) == 'total_mno_cost'] <- 'baseline'

perc_tech_cost_saving = merge(perc_tech_cost_saving, baseline, 
             by=c('country', 'scenario', 'confidence'),
             all.x=TRUE)

perc_tech_cost_saving$saving = round(
          (perc_tech_cost_saving$total_mno_cost - 
             perc_tech_cost_saving$baseline) / 
            perc_tech_cost_saving$total_mno_cost * 100)

# perc_tech_cost_saving <- perc_tech_cost_saving[!(perc_tech_cost_saving$scenario == "Baseline"),]

perc_tech_cost_saving = perc_tech_cost_saving %>%
  group_by(scenario, strategy, confidence) %>%
  summarize(
    saving = round(mean(saving)),
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

percentage_cost = data#[(data$scenario == 'baseline_10_10_10'),]

cost_composition = data

cost_composition$perc_network_cost = round((
  (cost_composition$ran + cost_composition$backhaul_fronthaul +
      cost_composition$civils + cost_composition$core_network) /
    cost_composition$total_mno_cost 
  ) * 100) 

cost_composition = cost_composition %>%
      group_by(strategy, scenario, confidence) %>%
      summarize(perc_network_cost = round(mean(perc_network_cost)))


data <- select(data, strategy, scenario, confidence, combined, ran, backhaul_fronthaul,
               civils, core_network, administration, spectrum_cost,
               tax, profit_margin, used_cross_subsidy, required_state_subsidy
               )

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

data <- gather(data, metric, value, ran:required_state_subsidy)#ran:profit_margin)#

data$metric = factor(data$metric, levels=c(
                                           "required_state_subsidy",
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
                                    labels=c(
                                             "Required State Subsidy",
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

network_costs <- data[!(data$metric == "User Cross-Subsidy" |
               data$metric == "Required State Subsidy"),]

network <- ggplot(network_costs, aes(x=strategy, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "Private Cost Composition for Broadband Universal Service", colour=NULL,
       subtitle = "Reported for a representative MNO delivering 10 Mbps broadband universal service",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=8, reverse = TRUE)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'c_cost_composition_baseline_national.png')
ggsave(path, units="in", width=7, height=7.5, dpi=300)
print(network)
dev.off()

percentage_cost = select(percentage_cost, country, scenario, strategy, confidence, 
                         total_mno_cost, used_cross_subsidy, 
                         required_state_subsidy)

percentage_cost$overall_cost = (percentage_cost$total_mno_cost + 
                                  percentage_cost$used_cross_subsidy + 
                                  percentage_cost$required_state_subsidy)

percentage_cost$perc_cross_subsidy = round((percentage_cost$used_cross_subsidy / 
                                              percentage_cost$overall_cost) * 100)

percentage_cost$perc_state_subsidy = round((percentage_cost$required_state_subsidy / 
                                              percentage_cost$overall_cost) * 100)

percentage_cost = select(percentage_cost, country, scenario, strategy, confidence, 
                         perc_cross_subsidy, perc_state_subsidy)

percentage_cost = percentage_cost %>%
  group_by(scenario, strategy, confidence) %>%
  summarize(
    perc_cross_subsidy = round(mean(perc_cross_subsidy)),
    perc_state_subsidy = round(mean(perc_state_subsidy)),
  )

###################Cost to Government
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_mno_cost_results_technology_options.csv'))

data <- data[!(data$total_mno_cost == "NA"),]
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

govt_costs = ggplot(data, aes(x=strategy, y=round(government_cost/1e9,1), 
                              group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(government_cost/1e9,1)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_brewer(palette="Dark2", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "Net Government Cost for Broadband Universal Service", colour=NULL,
       subtitle = "Reported for all scenarios and strategies for 10 Mbps broadband universal service",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(min_value-.5, max_value+4)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'd_government_costs.png')
ggsave(path, units="in", width=7, height=5, dpi=300)
print(govt_costs)
dev.off()

remove(data)

################## BUSINESS MODELS
#load data
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'decile_mno_results_business_model_options.csv'))

data <- data[!(data$total_mno_cost == "NA"),]
# data <- data[(data$integration == "baseline"),]
data <- data[!(data$strategy == "4G_epc_wireless_cns_baseline_baseline_baseline_baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

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
  labs(title = "Impact of Infrastructure Sharing on Cumulative Private Cost", colour=NULL,
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

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'national_mno_cost_results_business_model_options.csv'))
data <- data[!(data$strategy == "4G_epc_wireless_cns_baseline_baseline_baseline_baseline"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$overall_cost = (data$total_mno_cost + 
                       data$used_cross_subsidy + 
                       data$required_state_subsidy)

baseline = data[(
    data$strategy == '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline' 
),]
baseline = select(baseline, country, scenario, confidence, overall_cost)
names(data)[names(data) == 'overall_cost'] <- 'baseline'

data = merge(data, baseline, 
             by=c('country', 'scenario', 'confidence'),
             all.x=TRUE)

data$strategy = factor(data$strategy, 
levels=c("Revenue",
         "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
         "4G_epc_wireless_pss_baseline_baseline_baseline_baseline",
         "4G_epc_wireless_psb_baseline_baseline_baseline_baseline",
         "4G_epc_wireless_moran_baseline_baseline_baseline_baseline",
         "4G_epc_wireless_baseline_srn_baseline_baseline_baseline"
),
labels=c("Revenue",
         "Baseline (No sharing)",
         "Passive Site Sharing",
         "Passive Backhaul Sharing",
         "Active Sharing",
         "Shared Rural Network"
))
infra_sharing_perc_savings = select(data, country, scenario, strategy, 
                                    confidence, overall_cost, baseline)

infra_sharing_perc_savings$perc_cost_saving = round(
                      abs((infra_sharing_perc_savings$baseline - 
                           infra_sharing_perc_savings$overall_cost) / 
                           infra_sharing_perc_savings$baseline) * 100)

infra_sharing_perc_savings <- infra_sharing_perc_savings[!(
        infra_sharing_perc_savings$strategy == "Baseline (No sharing)"),]

infra_sharing_perc_savings = infra_sharing_perc_savings %>% 
  arrange(country, scenario, strategy, confidence)

infra_sharing_perc_savings = infra_sharing_perc_savings %>%
  group_by(scenario, strategy, confidence) %>%
  summarize(
    perc_cost_saving = round(mean(perc_cost_saving)),
  )

remove(data, baseline)

# ###################DECILE COST PROFILE FOR BASELINE
# folder <- dirname(rstudioapi::getSourceEditorContext()$path)
#
# #load data
# data <- read.csv(file.path(folder, '..', 'results', 'decile_mno_cost_results_technology_options.csv'))
#
# data <- data[!(data$total_mno_cost == "NA"),]
# data <- data[(data$confidence == 50),]
# # data <- data[(data$integration == "baseline"),]
# data <- data[(data$scenario == "baseline_10_10_10"),]
#
# names(data)[names(data) == 'GID_0'] <- 'country'
#
# data$combined <- paste(data$country, data$strategy, sep="_")
#
# data <- select(data, combined, decile, ran, backhaul_fronthaul,
#                civils, core_network, administration, #acquisition_per_subscriber,
#                spectrum_cost, tax, profit_margin,
#                used_cross_subsidy, required_state_subsidy)
#
# data$combined = factor(data$combined,
#                        levels=c(
#                          "CIV_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "CIV_3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "CIV_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "CIV_4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "KEN_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "KEN_3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "KEN_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "KEN_4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "MLI_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "MLI_3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "MLI_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "MLI_4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "SEN_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "SEN_3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "SEN_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "SEN_4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "TZA_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "TZA_3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "TZA_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "TZA_4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "UGA_3G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "UGA_3G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
#                          "UGA_4G_epc_fiber_baseline_baseline_baseline_baseline_baseline",
#                          "UGA_4G_epc_wireless_baseline_baseline_baseline_baseline_baseline"
#                        ),
#                        labels=c("Cote D'Ivoire 3G (FB)",
#                                 "Cote D'Ivoire 3G (W)",
#                                 "Cote D'Ivoire 4G (FB)",
#                                 "Cote D'Ivoire 4G (W)",
#                                 "Mali 3G (FB)",
#                                 "Mali 3G (W)",
#                                 "Mali 4G (FB)",
#                                 "Mali 4G (W)",
#                                 "Senegal 3G (FB)",
#                                 "Senegal 3G (W)",
#                                 "Senegal 4G (FB)",
#                                 "Senegal 4G (W)",
#                                 "Kenya 3G (FB)",
#                                 "Kenya 3G (W)",
#                                 "Kenya 4G (FB)",
#                                 "Kenya 4G (W)",
#                                 "Tanzania 3G (FB)",
#                                 "Tanzania 3G (W)",
#                                 "Tanzania 4G (FB)",
#                                 "Tanzania 4G (W)",
#                                 "Uganda 3G (FB)",
#                                 "Uganda 3G (W)",
#                                 "Uganda 4G (FB)",
#                                 "Uganda 4G (W)"))
#
# data <- gather(data, metric, value, ran:required_state_subsidy)
#
# data$metric = factor(data$metric, levels=c("required_state_subsidy",
#                                            "used_cross_subsidy",
#                                            "profit_margin",
#                                            "tax",
#                                            "spectrum_cost",
#                                            "administration",
#                                            "ran",
#                                            'backhaul_fronthaul',
#                                            'civils',
#                                            'core_network'
# ),
# labels=c("Required State Subsidy",
#          "User Cross-Subsidy",
#          "Profit",
#          "Tax",
#          "Spectrum",
#          "Administration",
#          "RAN",
#          "Backhaul",
#          "Civils",
#          'Core/Regional Fiber'
# ))
#
# panel <- ggplot(data, aes(x=decile, y=(value/1e9), group=metric, fill=metric)) +
#   geom_bar(stat = "identity") +
#   scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
#   theme(legend.position = "bottom") +
#   labs(title = "Decile Cost Composition by Strategy and Country", colour=NULL,
#        subtitle = "Illustrates required state subsidy under baseline conditions",
#        x = NULL, y = "Total Cost (Billions $USD)") +
#   scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
#   guides(fill=guide_legend(ncol=6, reverse = TRUE)) +
#   facet_wrap(~combined, scales = "free", ncol=4)
#
# path = file.path(folder, 'figures', 'cost_composition_baseline_decile.png')
# ggsave(path, units="in", width=10, height=10, dpi=300)
# print(panel)
# dev.off()

# ################## INTEGRATION RESULTS
# folder <- dirname(rstudioapi::getSourceEditorContext()$path)
#
# #load data
# data <- read.csv(file.path(folder, '..', 'results', 'decile_results_integration_options.csv'))
#
# data <- data[!(data$total_mno_cost == "NA"),]
# # data <- data[(data$scenario == "baseline_10_10_10"),]
#
# names(data)[names(data) == 'GID_0'] <- 'country'
#
# sum_of_costs <- select(data, country, strategy, integration, total_mno_cost)
# sum_of_costs <- sum_of_costs %>%
#   group_by(country, strategy, integration) %>%
#   summarize(total_mno_cost_m = round(sum(total_mno_cost) / 1e6, 3))
#
# data$combined <- paste(data$country, data$strategy, sep="_")
#
# data <- select(data, combined, integration, decile, total_mno_cost)
#
# data$combined = factor(data$combined,
#                        levels=c(
#                          "CIV_3G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                         "CIV_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "CIV_4G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "CIV_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "KEN_3G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "KEN_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "KEN_4G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "KEN_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "MLI_3G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "MLI_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "MLI_4G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "MLI_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "SEN_3G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "SEN_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "SEN_4G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "SEN_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "TZA_3G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "TZA_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "TZA_4G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "TZA_4G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "UGA_3G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "UGA_3G_epc_fiber_baseline_baseline_baseline_baseline_integration",
#                         "UGA_4G_epc_wireless_baseline_baseline_baseline_baseline_integration",
#                          "UGA_4G_epc_fiber_baseline_baseline_baseline_baseline_integration"
#                        ),
#                        labels=c("Cote D'Ivoire 3G (W)",
#                                 "Cote D'Ivoire 3G (FB)",
#                                 "Cote D'Ivoire 4G (W)",
#                                 "Cote D'Ivoire 4G (FB)",
#                                 "Mali 3G (W)",
#                                 "Mali 3G (FB)",
#                                 "Mali 4G (W)",
#                                 "Mali 4G (FB)",
#                                 "Senegal 3G (W)",
#                                 "Senegal 3G (FB)",
#                                 "Senegal 4G (W)",
#                                 "Senegal 4G (FB)",
#                                 "Kenya 3G (W)",
#                                 "Kenya 3G (FB)",
#                                 "Kenya 4G (W)",
#                                 "Kenya 4G (FB)",
#                                 "Tanzania 3G (W)",
#                                 "Tanzania 3G (FB)",
#                                 "Tanzania 4G (W)",
#                                 "Tanzania 4G (FB)",
#                                 "Uganda 3G (W)",
#                                 "Uganda 3G (FB)",
#                                 "Uganda 4G (W)",
#                                 "Uganda 4G (FB)"))
#
# data$integration = factor(data$integration, levels=c("baseline",
#                                                "integration"),
# labels=c("Baseline",
#          "Regional Integration"
# ))
#
# data <- data[order(data$combined, data$decile, data$integration),]
#
# data <- data %>%
#   group_by(combined, decile, integration) %>%
#   mutate(cumulative_value_bn = cumsum(round(total_mno_cost / 1e9, 3)))
#
# panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=integration, group=integration)) +
#   geom_line() +
#   scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
#   theme(axis.text.x = element_text(angle = 45, hjust = 1),legend.position = "bottom") +
#   labs(title = "Impact of Regional Market Integration by Decile and Country", colour=NULL,
#        subtitle = "Results reported for all technologies",
#        x = 'Population Covered (%)', y = "Cumulative Cost (Billions $USD)") +
#   scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) +
#   scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
#   guides(colour=guide_legend(ncol=2)) +
#   facet_wrap(~combined, scales = "free", ncol=4)
#
# path = file.path(folder, 'figures', 'results_regional_integration_options_wrap.png')
# ggsave(path, units="in", width=10, height=10, dpi=300)
# print(panel)
# dev.off()
#
# savings <- spread(sum_of_costs, key = integration, value = total_mno_cost_m)
# savings$saving_usd <- savings$baseline - savings$integration
# savings$saving_perc <- (savings$saving_usd / savings$baseline) * 100
#
# path = file.path(folder, '..', 'results', 'integration_savings.csv')
# write.csv(savings, path)
#
# business_model_results <- savings %>%
#   group_by(strategy) %>%
#   summarise(
#     raw_min_m = round(min(saving_usd)),
#     raw_mean_m = round(mean(saving_usd)),
#     raw_max_m = round(max(saving_usd)),
#     perc_min_m = round(min(saving_perc)),
#     perc_mean_m = round(mean(saving_perc)),
#     perc_max_m = round(max(saving_perc)),
#   )
#
