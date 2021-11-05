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
  scale_color_manual(values=c("#009E73", "#F0E442","#E69F00", 
                              "#56B4E9","#D55E00", "#0072B2")) + 
  geom_vline(xintercept=2020, linetype="dashed", color = "grey", size=.5) +
  scale_x_continuous(expand = c(0, 0.5), limits = c(2010,2030), 
                     breaks = seq(2010,2030,2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), 
        legend.position = "bottom", legend.title=element_blank()) +
  labs(title = "(A) Mobile Subscriptions by Country", 
       x = NULL, y = "Subscribers (%)") +
  guides(shape=guide_legend(ncol=6), colour=guide_legend(ncol=6)) +
  facet_grid(~scenario)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, 'smartphones', "data_inputs")

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

data$settlement_type = factor(data$settlement_type,
                              levels=c("urban",
                                       "rural"),
                              labels=c("Urban",
                                       "Rural"))

data = data[complete.cases(data),]

smartphones = ggplot(data, aes(x=year, y=penetration, group=country)) +
  geom_point(aes(shape=country, color=country), size=1) +
  geom_line(aes(color=country)) +
  scale_shape_manual(values=c(0, 1, 2, 3, 4, 5)) +
  scale_color_manual(values=c("#009E73", "#F0E442","#E69F00", 
                              "#56B4E9","#D55E00", "#0072B2")) + 
  scale_x_continuous(expand = c(0, 0.25), limits = c(2020,2030), 
                     breaks = seq(2020,2030,2)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0,100)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), 
        legend.position = "bottom", legend.title=element_blank()) +
  labs(title = "(B) Smartphone Penetration by Country", 
       x = NULL, y = "Smartphones (%)") +
  guides(shape=guide_legend(ncol=6), colour=guide_legend(ncol=6)) +
  facet_grid(settlement_type~scenario)


combined <- ggarrange(subscriptions, smartphones, 
                      ncol = 1, nrow = 2,
                      common.legend = TRUE, 
                      legend='bottom', heights=c(3.5, 5))

path = file.path(folder, 'figures', 'a_demand_graphic.png')
ggsave(path, units="in", width=7, height=5.5, dpi=300)
print(combined)
dev.off()

remove(subscriptions, smartphones, combined, data)

###################################################################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', filename))

data <- data[grep("10_10_10", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, financial_cost)

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

min_value = round(min(data$financial_cost)/1e9,0)
max_value = round(max(data$financial_cost)/1e9,0)

financial_cost_10mbps = ggplot(data, 
  aes(x=strategy, y=round(financial_cost/1e9), 
      group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(financial_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(
  title="(A) Financial Cost of Universal Broadband by Technology (10 Mbps Per User)", 
       colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

############################################################
#load data
filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', filename))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, financial_cost)

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

min_value = round(min(data$financial_cost)/1e9,0)
max_value = round(max(data$financial_cost)/1e9,0)

financial_cost_2mbps = ggplot(data, aes(x=strategy, y=round(financial_cost/1e9), 
                                     group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(financial_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(title = "(B) Financial Cost of Universal Broadband by Technology (2 Mbps Per User)", 
       colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(financial_cost_10mbps, financial_cost_2mbps,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'b_financial_cost_by_technology.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

############################################################
###################Cost to Government
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', filename))

data <- data[grep("10_10_10", data$scenario), ]
data <- data[!(data$government_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

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

govt_costs_10mbps = ggplot(data, aes(x=strategy, 
   y=round(government_cost/1e9,1), group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(government_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-1) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(title="(A) Net Government Cost for Universal Broadband by Technology (10 Mbps Per User)", 
       colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), 
                     limits = c(min_value-.5, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

############################################################
#load data
filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', filename))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$government_cost == "NA"),]
data <- data[(data$confidence == 50),]

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

govt_costs_2mbps = ggplot(data, aes(x=strategy, 
    y=round(government_cost/1e9,1), group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(government_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-1) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(title="(B) Net Government Cost for Universal Broadband by Technology (2 Mbps Per User)", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), 
                     limits = c(min_value-.5, max_value+15)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(govt_costs_10mbps, govt_costs_2mbps,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'c_govt_cost_by_technology.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

############################################################
###Business model
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'national_market_results_business_model_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', filename))

data <- data[grep("10_10_10", data$scenario), ]
data <- data[!(data$total_market_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, financial_cost)

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
  "4G_epc_wireless_srn_srn_baseline_baseline_baseline",
  "4G_epc_wireless_moran_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_psb_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline"
),
labels=c(
  "SRN",
  "Active",
  "Passive",
  "Baseline"
))

data <- data[complete.cases(data),]

min_value = round(min(data$financial_cost)/1e9,2)
max_value = round(max(data$financial_cost)/1e9,2)

cost_10mbps = ggplot(data, aes(x=strategy, y=round(financial_cost/1e9), 
                               group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(financial_cost/1e9, 1)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.5) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(title = "(A) Financial Cost of Universal Broadband with Infrastructure Sharing (10 Mbps Per User)", 
       colour=NULL,
       subtitle = "Reported for all scenarios and strategies using 4G (Wireless)",
       x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

######################################################################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'national_market_results_business_model_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', filename))

data <- data[grep("2_2_2", data$scenario), ]
data <- data[!(data$financial_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, country, scenario, strategy, financial_cost)

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
  "4G_epc_wireless_srn_srn_baseline_baseline_baseline",
  "4G_epc_wireless_moran_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_psb_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline"
),
labels=c(
  "SRN",
  "Active",
  "Passive",
  "Baseline"
))

data <- data[complete.cases(data),]

min_value = round(min(data$financial_cost)/1e9,2)
max_value = round(max(data$financial_cost)/1e9,2)

cost_2mbps = ggplot(data, aes(x=strategy, y=round(financial_cost/1e9), 
                              group=scenario, fill=scenario)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(financial_cost/1e9, 1)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.5) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(title = "(B) Financial Cost of Universal Broadband with Infrastructure Sharing (2 Mbps Per User)", 
       colour=NULL,
       subtitle = "Reported for all scenarios and strategies using 4G (Wireless)",
       x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(cost_10mbps, cost_2mbps,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'd_infra_sharing_cost.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

#########################################################################
#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, '..', 'results', 'user_costs')

data1 <- read.csv(file.path(folder_inputs, 'total_cost_estimates_2.csv'))
data1$Capacity = '2 Mbps Per User'

data2 <- read.csv(file.path(folder_inputs, 'total_cost_estimates_10.csv'))
data2$Capacity = '10 Mbps Per User'

data = rbind(data1, data2)

remove(data1, data2)

data <- data[(data$Confidence == 50),]

data <- select(data, Scenario, Strategy, Capacity, 
               Private.Cost...Bn., Government.Cost...Bn.,
               Financial.Cost...Bn.)


data$Scenario = factor(data$Scenario, levels=c("Low",
                                               "Baseline",
                                               "High"))

data$Capacity = factor(data$Capacity, levels=c("10 Mbps Per User",
                                               "2 Mbps Per User"
))

totals <- data %>%
  group_by(Scenario, Strategy, Capacity) %>%
  summarize(financial_cost = round(
    (Private.Cost...Bn. + Government.Cost...Bn.)/1000, 1))

colnames(data)[colnames(data) == 'Private.Cost...Bn.'] <- 'Private Cost ($USD)'
colnames(data)[colnames(data) == 'Government.Cost...Bn.'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'Financial.Cost...Bn.'] <- 'financial_cost'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Cost ($USD)', 
                        'Government Cost ($USD)', 
)

min_value = min(round(data$financial_cost/1e3, 2))
max_value = max(round(data$financial_cost/1e3, 2))

data$value = round(data$value/1e3, 2)

ggplot(data, aes(y=value, x=Strategy, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(Strategy, financial_cost, label = financial_cost, fill = NULL), 
            size = 2.5, data = totals, hjust=-.5) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(title = "Financial Cost of Universal Broadband Across Africa by Technology", colour=NULL,
       subtitle = "Reported for all scenarios and strategies",
       x = NULL, y = "Financial Cost (Trillions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-min_value, max_value+0.5)) + 
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(Capacity~Scenario)

path = file.path(folder, 'figures', 'f_total_financial_cost_across_Africa.png')
ggsave(path, units="in", width=8, height=5, dpi=300)
dev.off()

#############################
###VISUALISE MODEL OUTPUTS###
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
filename = 'national_market_results_sensitivity_analysis.csv'
data <- read.csv(file.path(folder, '..', 'results', 
                           'sensitivity_analysis', filename))
unique(data$strategy)

data = data %>% 
  separate(scenario, into = c("scenario", "capacity", NA, NA), sep="_") %>% 
  separate(strategy, into = c("generation", "core", "backhaul", 
                              NA, NA, NA, NA, "obf", "costs"), sep="_")


data$strategy = paste(data$generation, data$backhaul, sep='_')

data = data[data$strategy == "4G_wireless",]
data = data[data$scenario == "baseline",]
data = data[data$capacity == "10",]

data$GID_0 = factor(data$GID_0, levels=c("CIV",
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

data$obf = factor(data$obf, levels=c('10', '20', '30' ),
                  labels=c('-50%', 'Baseline', '+50%'))

data$costs = factor(data$costs, levels=c('125', '100', '75'),
                    labels=c('+25%', 'Baseline', '-25%'))

data = select(data, GID_0, scenario, obf, costs, financial_cost)

data_obf = data[data$costs == "Baseline",]

min_value = round(min(data_obf$financial_cost)/1e9,0)
max_value = round(max(data_obf$financial_cost)/1e9,0)

obf_figure = ggplot(data_obf, 
                    aes(x=GID_0, y=round(financial_cost/1e9),
                        group=obf, fill=obf)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(financial_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(
    title="(A) Cost Sensitivity for Active Network Users when Maintaining QoS", 
    colour=NULL,
    subtitle = "Reported for 4G (W) targetting ~10 Mbps Per User",
    x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) 

data_costs = data[data$obf == "Baseline",]

min_value = round(min(data_costs$financial_cost)/1e9,0)
max_value = round(max(data_costs$financial_cost)/1e9,0)

costs_figure = ggplot(data_costs, 
                      aes(x=GID_0, y=round(financial_cost/1e9),
                          group=costs, fill=costs)) +
  geom_bar(stat = "identity", position=position_dodge()) +
  geom_text(aes(label = round(financial_cost/1e9)), size = 2.5,
            position = position_dodge(width = 1), hjust=-.25) + 
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  theme(legend.position = "bottom") +
  labs(
    title="(B) Cost Sensitivity to Model Input Costs", 
    colour=NULL,
    subtitle = "Reported for 4G (W) targetting ~10 Mbps Per User",
    x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+17)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) 

combined <- ggarrange(obf_figure, costs_figure,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'sensitivity_analysis.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()
