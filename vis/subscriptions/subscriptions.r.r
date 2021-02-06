#Spectrum costs
library(tidyverse)
library(ggpubr)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, "data_inputs")

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

data$scenario = factor(data$scenario, levels=c("high",
                                             'baseline',
                                             "low"
                                             ),
                      labels=c("High (3% CAGR)",
                               "Baseline (2% CAGR)",
                               "Low (1% CAGR)"
                      ))

data = data[complete.cases(data),]

subscriptions = ggplot(data, aes(x=year, y=penetration, group=country)) +
  geom_point(aes(shape=country, color=country), size=2.5) +
  geom_line(aes(color=country)) +
  scale_shape_manual(values=c(0, 1, 2, 3, 4, 5, 6, 7, 8)) +
  scale_color_manual(values=c("#F0E442", "#F0E442","#E69F00", "#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73"))+
  geom_vline(xintercept=2020, linetype="dashed", color = "grey", size=.5) +
  # annotate("text", x = 2018, y = 15, label = "Historical", vjust=-1, angle = 0) +
  # annotate("text", x = 2022, y = 15, label = "Forecast", vjust=-1, angle = 0) +
  scale_x_continuous(expand = c(0, 0), limits = c(2010,2030), 
                     breaks = seq(2010,2030,2)) +
  # scale_y_continuous(expand = c(0, 0), limits = c(0,95)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), 
        legend.position = "bottom", legend.title=element_blank()) +
  labs(title = "(A) Mobile Subscriptions by Country", 
       # subtitle = "Historical: 2010-2020. Forecast: 2020-2030 ",
       x = NULL, y = "Unique Subscribers (%)") +
  guides(shape=guide_legend(ncol=6), colour=guide_legend(ncol=6)) +
  facet_wrap(~scenario, ncol=3, scales='free_y')

path = file.path(folder, 'figures', 'cell_subscriptions.png')
ggsave(path, units="in", width=8, height=5, dpi=300)
print(subscriptions)
dev.off()

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, "..", "smartphones", "data_inputs")

# files = list.files(path=folder_inputs, pattern="*.csv")

files = c("CIV.csv", "KEN.csv", "MLI.csv", "SEN.csv", "TZA.csv", "UGA.csv") 

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

data$scenario = factor(data$scenario, levels=c("high",
                                               'baseline',
                                               "low"
),
labels=c("High",
         "Baseline",
         "Low"
))

data$settlement_type = factor(data$settlement_type, 
                              levels=c("urban",
                                       'rural'),
                              labels=c("Urban",
                                       "Rural"
))

data = data[complete.cases(data),]

smartphones = ggplot(data, aes(x=year, y=penetration, group=country)) +
  geom_point(aes(shape=country, color=country), size=2.5) +
  geom_line(aes(color=country)) +
  scale_shape_manual(values=c(0, 1, 2, 3, 4, 5, 6, 7, 8)) +
  scale_color_manual(values=c("#F0E442", "#F0E442","#E69F00", "#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73")) +
  # geom_vline(xintercept=2020, linetype="dashed", color = "grey", size=.5) +
  scale_x_continuous(expand = c(0, 0.25), limits = c(2020,2030), 
                     breaks = seq(2020,2030,2)) +
  # scale_y_continuous(expand = c(0, 0), limits = c(0,95)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), 
        legend.position = "bottom", legend.title=element_blank()) +
  labs(title = "(B) Smartphone Penetration by Country", 
       # subtitle = "Forecast: 2020-2030",
       x = NULL, y = "Smartphones (%)") +
  guides(shape=guide_legend(ncol=6), colour=guide_legend(ncol=6)) +
  facet_wrap(settlement_type~scenario, ncol=3, scales='free_y')

path = file.path(folder, 'figures', 'cell_subscriptions.png')
ggsave(path, units="in", width=8, height=5, dpi=300)
print(subscriptions)
dev.off()

combined <- ggarrange(subscriptions, smartphones, 
                      ncol = 1, nrow = 2,
                      common.legend = TRUE, 
                      legend='bottom', heights=c(3.5, 6))

path = file.path(folder, '..', 'figures', 'a_demand_graphic.png')
ggsave(path, units="in", width=6, height=6.5, dpi=300)
print(combined)
dev.off()
