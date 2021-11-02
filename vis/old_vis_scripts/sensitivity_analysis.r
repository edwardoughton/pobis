###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

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
