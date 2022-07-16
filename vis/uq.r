###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

###################################################################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

path = file.path(folder, '..', 'results', 'model_results', 'national_results')
setwd(path)
files = list.files(pattern="*.csv")
data = do.call(rbind, lapply(files, function(x) read.csv(x, stringsAsFactors = FALSE)))

names(data)[names(data) == 'GID_0'] <- 'country'
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
data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'High'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'Low'
data$scenario_adopt = factor(data$scenario_adopt,
                             levels=c("Low",
                                "Baseline",
                                "High"))

data$scenario_capacity = ''
data$scenario_capacity[grep("10_10_10", data$scenario)] = '10 GB/Month'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 GB/Month'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30 GB/Month'

data$strategy_short = ""
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("3G_epc_fiber", data$strategy)] = '3G (F)'
data$strategy_short[grep("3G_epc_wireless", data$strategy)] = '3G (W)'

###################

sample <- data[(data$scenario_capacity == '10 GB/Month'),]

sample <- select(sample, country, scenario_adopt, strategy_short, input_cost, financial_cost)

sample$financial_cost = round(sample$financial_cost / 1e9, 1)

min_value = min(sample$financial_cost)
max_value = max(sample$financial_cost)

sample = spread(sample, input_cost, financial_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 1))

financial_cost_10gb = ggplot(sample,
         aes(x=strategy_short, y=baseline, group=scenario_adopt, fill=scenario_adopt)) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5,
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title="(A) Financial NPV Cost of Universal Broadband by Technology (10 GB/Month Per User)",
    colour=NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
    scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
    facet_wrap(~country, scales = "free", ncol=3)

  
sample <- data[(data$scenario_capacity == '30 GB/Month'),]

sample <- select(sample, country, scenario_adopt, strategy_short, input_cost, financial_cost)

sample$financial_cost = round(sample$financial_cost / 1e9, 1)

min_value = min(sample$financial_cost)
max_value = max(sample$financial_cost)

sample = spread(sample, input_cost, financial_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 1))

financial_cost_30gb = ggplot(sample,
       aes(x=strategy_short, y=baseline, group=scenario_adopt, fill=scenario_adopt)) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5,
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title="(B) Financial NPV Cost of Universal Broadband by Technology (30 GB/Month Per User)",
    colour=NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(financial_cost_10gb, financial_cost_30gb,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'b_financial_cost_by_technology.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

########################

###################

sample <- data[(data$scenario_capacity == '10 GB/Month'),]

sample <- select(sample, country, scenario_adopt, strategy_short, input_cost, government_cost)

sample$government_cost = round(sample$government_cost / 1e9, 1)

min_value = min(sample$government_cost)
max_value = max(sample$government_cost)

sample = spread(sample, input_cost, government_cost)

sample$low[sample$low < 0] = 0
sample$baseline[sample$baseline < 0] = 0
sample$high[sample$high < 0] = 0

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 1))

government_cost_10gb = 
  ggplot(sample,
   aes(x=strategy_short, y=baseline, group=scenario_adopt, fill=scenario_adopt)) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5,
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title="(A) Net Government NPV Cost of Universal Broadband by Technology (10 GB/Month Per User)",
    colour=NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  facet_wrap(~country, scales = "free", ncol=3)


sample <- data[(data$scenario_capacity == '30 GB/Month'),]

sample <- select(sample, country, scenario_adopt, strategy_short, input_cost, government_cost)

sample$government_cost = round(sample$government_cost / 1e9, 1)

min_value = min(sample$government_cost)
max_value = max(sample$government_cost)

sample = spread(sample, input_cost, government_cost)

sample$low[sample$low < 0] = 0
sample$baseline[sample$baseline < 0] = 0
sample$high[sample$high < 0] = 0

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 1))

government_cost_30gb = ggplot(sample,
                             aes(x=strategy_short, y=baseline, group=scenario_adopt, fill=scenario_adopt)) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5,
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title="(B) Net Government NPV Cost of Universal Broadband by Technology (30 GB/Month Per User)",
    colour=NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6", "#5D3A9B"), name=NULL) +
  facet_wrap(~country, scales = "free", ncol=3)

combined <- ggarrange(government_cost_10gb, government_cost_30gb,   
                      ncol = 1, nrow = 2)

path = file.path(folder, 'figures', 'c_govt_cost_by_technology.png')
ggsave(path, units="in", width=8, height=11, dpi=300)
print(combined)
dev.off()

########################