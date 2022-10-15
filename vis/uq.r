###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

###################################################################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

path = file.path(folder, '..', 'results', 'model_results', 'national_results')
setwd(path)
files = list.files(pattern = "*.csv")
data = do.call(rbind, lapply(files, function(x)
  read.csv(x, stringsAsFactors = FALSE)))

names(data)[names(data) == 'GID_0'] <- 'country'
data$country = factor(
  data$country,
  levels = c("CIV",
             'MLI',
             "SEN",
             "KEN",
             "TZA",
             "UGA"),
  labels = c(
    "Cote D'Ivoire",
    "Mali",
    "Senegal",
    "Kenya",
    "Tanzania",
    "Uganda"
  )
)
data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'High'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'Low'
data$scenario_adopt = factor(data$scenario_adopt,
                             levels = c("Low",
                                        "Baseline",
                                        "High"))

data$scenario_capacity = ''
data$scenario_capacity[grep("10_10_10", data$scenario)] = '10 GB/Month'
# data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 GB/Month'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30 GB/Month'

data$strategy_short = ""
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("3G_epc_fiber", data$strategy)] = '3G (F)'
data$strategy_short[grep("3G_epc_wireless", data$strategy)] = '3G (W)'

data$sharing_strategy = ""
data$sharing_strategy[grep("baseline_baseline_baseline_baseline", data$strategy)] = 'Baseline'
data$sharing_strategy[grep("psb_baseline_baseline_baseline_baseline", data$strategy)] = 'Passive'
data$sharing_strategy[grep("moran_baseline_baseline_baseline_baseline", data$strategy)] = 'Active'
data$sharing_strategy[grep("srn_srn_baseline_baseline_baseline", data$strategy)] = 'SRN'

data$sharing_strategy = factor(data$sharing_strategy,
                               levels = c("SRN",
                                          "Active",
                                          "Passive",
                                          "Baseline"))

###################

sample <- data[(data$scenario_capacity == '30 GB/Month'), ]
sample <- sample[(sample$sharing_strategy == 'Baseline'), ]
sample = sample %>% distinct(country,
                             scenario_adopt,
                             strategy_short,
                             input_cost,
                             financial_cost)

sample <-
  select(sample,
         country,
         scenario_adopt,
         strategy_short,
         input_cost,
         financial_cost)

sample$financial_cost = round(sample$financial_cost / 1e9, 1)

min_value = min(sample$financial_cost)
max_value = max(sample$financial_cost)

sample = unique(sample)

sample = spread(sample, input_cost, financial_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round((baseline), 1))

financial_cost_30gb = ggplot(
  sample,
  aes(
    x = strategy_short,
    y = baseline,
    group = scenario_adopt,
    fill = scenario_adopt
  )
) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(
    data = sample,
    aes(y = baseline, ymin = low, ymax = high),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title = "(B) Financial PV of Universal Broadband by Technology (30 GB/Month Per User)",
    colour = NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL,
    y = "Financial Cost (Billions $USD)"
  ) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill = guide_legend(ncol = 3, reverse = TRUE)) +
  scale_fill_manual(values = c("#E1BE6A", "#40B0A6", "#5D3A9B"),
                    name = NULL) +
  facet_wrap( ~ country, scales = "free", ncol = 3)

sample <- data[(data$scenario_capacity == '10 GB/Month'), ]
sample <- sample[(sample$sharing_strategy == 'Baseline'), ]
sample = sample %>% distinct(country,
                             scenario_adopt,
                             strategy_short,
                             input_cost,
                             financial_cost)

sample <-
  select(sample,
         country,
         scenario_adopt,
         strategy_short,
         input_cost,
         financial_cost)

sample$financial_cost = round(sample$financial_cost / 1e9, 1)

sample = spread(sample, input_cost, financial_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round((baseline), 1))

financial_cost_10gb = ggplot(
  sample,
  aes(
    x = strategy_short,
    y = baseline,
    group = scenario_adopt,
    fill = scenario_adopt
  )
) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(
    data = sample,
    aes(y = baseline, ymin = low, ymax = high),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title = "(A) Financial PV of Universal Broadband by Technology (10 GB/Month Per User)",
    colour = NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL,
    y = "Financial Cost (Billions $USD)"
  ) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill = guide_legend(ncol = 3, reverse = TRUE)) +
  scale_fill_manual(values = c("#E1BE6A", "#40B0A6", "#5D3A9B"),
                    name = NULL) +
  facet_wrap( ~ country, scales = "free", ncol = 3)


combined <- ggarrange(financial_cost_10gb,
                      financial_cost_30gb,
                      ncol = 1,
                      nrow = 2)

path = file.path(folder, 'figures', 'b_financial_cost_by_technology.png')
ggsave(
  path,
  units = "in",
  width = 8,
  height = 11,
  dpi = 300
)
print(combined)
dev.off()

########################

###################

sample <- data[(data$scenario_capacity == '30 GB/Month'), ]
sample <- sample[(sample$sharing_strategy == 'Baseline'), ]
sample = sample %>% distinct(country,
                             scenario_adopt,
                             strategy_short,
                             input_cost,
                             government_cost)

sample <-
  select(sample,
         country,
         scenario_adopt,
         strategy_short,
         input_cost,
         government_cost)

sample$government_cost = round(sample$government_cost / 1e9, 1)

min_value = min(sample$government_cost)
max_value = max(sample$government_cost)

sample = unique(sample)

sample = spread(sample, input_cost, government_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round((baseline), 1))

government_cost_30gb = ggplot(
  sample,
  aes(
    x = strategy_short,
    y = baseline,
    group = scenario_adopt,
    fill = scenario_adopt
  )
) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(
    data = sample,
    aes(y = baseline, ymin = low, ymax = high),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title = "(B) Net Government Cost of Universal Broadband by Technology (30 GB/Month Per User)",
    colour = NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL,
    y = "Financial Cost (Billions $USD)"
  ) +
  scale_y_continuous(expand = c(0, 0),
                     limits = c(min_value, max_value)) +
  guides(fill = guide_legend(ncol = 3, reverse = TRUE)) +
  scale_fill_manual(values = c("#E1BE6A", "#40B0A6", "#5D3A9B"),
                    name = NULL) +
  facet_wrap( ~ country, scales = "free", ncol = 3)

sample <- data[(data$scenario_capacity == '10 GB/Month'), ]
sample <- sample[(sample$sharing_strategy == 'Baseline'), ]
sample = sample %>% distinct(country,
                             scenario_adopt,
                             strategy_short,
                             input_cost,
                             government_cost)

sample <-
  select(sample,
         country,
         scenario_adopt,
         strategy_short,
         input_cost,
         government_cost)

sample$government_cost = round(sample$government_cost / 1e9, 1)

sample = unique(sample)

sample = spread(sample, input_cost, government_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, strategy_short) %>%
  summarize(value2 = round((baseline), 1))

government_cost_10gb = ggplot(
  sample,
  aes(
    x = strategy_short,
    y = baseline,
    group = scenario_adopt,
    fill = scenario_adopt
  )
) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(
    data = sample,
    aes(y = baseline, ymin = low, ymax = high),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title = "(A) Net Government Cost of Universal Broadband by Technology (10 GB/Month Per User)",
    colour = NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL,
    y = "Financial Cost (Billions $USD)"
  ) +
  scale_y_continuous(expand = c(0, 0),
                     limits = c(min_value, max_value)) +
  guides(fill = guide_legend(ncol = 3, reverse = TRUE)) +
  scale_fill_manual(values = c("#E1BE6A", "#40B0A6", "#5D3A9B"),
                    name = NULL) +
  facet_wrap( ~ country, scales = "free", ncol = 3)


combined <- ggarrange(government_cost_10gb,
                      government_cost_30gb,
                      ncol = 1,
                      nrow = 2)

path = file.path(folder, 'figures', 'c_govt_cost_by_technology.png')
ggsave(
  path,
  units = "in",
  width = 8,
  height = 11,
  dpi = 300
)
print(combined)
dev.off()

########################
###################

sample <- data[(data$scenario_capacity == '30 GB/Month'), ]
sample <- sample[(sample$strategy_short == '4G (W)'), ]
sample = sample %>% distinct(country,
                             scenario_adopt,
                             sharing_strategy,
                             input_cost,
                             financial_cost)

sample <-
  select(sample,
         country,
         scenario_adopt,
         sharing_strategy,
         input_cost,
         financial_cost)

sample$financial_cost = round(sample$financial_cost / 1e9, 1)

min_value = min(sample$financial_cost)
max_value = max(sample$financial_cost)

sample = unique(sample)

sample = spread(sample, input_cost, financial_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, sharing_strategy) %>%
  summarize(value2 = round((baseline), 1))

financial_cost_30gb = ggplot(
  sample,
  aes(
    x = sharing_strategy,
    y = baseline,
    group = scenario_adopt,
    fill = scenario_adopt
  )
) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(
    data = sample,
    aes(y = baseline, ymin = low, ymax = high),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title = "(B) Financial PV using Infrastructure Sharing (30 GB/Month Per User)",
    colour = NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL,
    y = "Financial Cost (Billions $USD)"
  ) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill = guide_legend(ncol = 3, reverse = TRUE)) +
  scale_fill_manual(values = c("#E1BE6A", "#40B0A6", "#5D3A9B"),
                    name = NULL) +
  facet_wrap( ~ country, scales = "free", ncol = 3)


sample <- data[(data$scenario_capacity == '10 GB/Month'), ]
sample <- sample[(sample$strategy_short == '4G (W)'), ]
sample = sample %>% distinct(country,
                             scenario_adopt,
                             sharing_strategy,
                             input_cost,
                             financial_cost)

sample <-
  select(sample,
         country,
         scenario_adopt,
         sharing_strategy,
         input_cost,
         financial_cost)

sample$financial_cost = round(sample$financial_cost / 1e9, 1)

sample = spread(sample, input_cost, financial_cost)

totals <- sample %>%
  group_by(country, scenario_adopt, sharing_strategy) %>%
  summarize(value2 = round((baseline), 1))

financial_cost_10gb = ggplot(
  sample,
  aes(
    x = sharing_strategy,
    y = baseline,
    group = scenario_adopt,
    fill = scenario_adopt
  )
) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(
    data = sample,
    aes(y = baseline, ymin = low, ymax = high),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  coord_flip() +
  theme(legend.position = 'bottom') +
  labs(
    title = "(A) Financial PV using Infrastructure Sharing (10 GB/Month Per User)",
    colour = NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios.",
    x = NULL,
    y = "Financial Cost (Billions $USD)"
  ) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill = guide_legend(ncol = 3, reverse = TRUE)) +
  scale_fill_manual(values = c("#E1BE6A", "#40B0A6", "#5D3A9B"),
                    name = NULL) +
  facet_wrap( ~ country, scales = "free", ncol = 3)

combined <- ggarrange(financial_cost_10gb,
                      financial_cost_30gb,
                      ncol = 1,
                      nrow = 2)

path = file.path(folder, 'figures', 'd_infra_sharing_cost.png')
ggsave(
  path,
  units = "in",
  width = 8,
  height = 11,
  dpi = 300
)
print(combined)
dev.off()

########################
########################



#########################################################################
#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, '..', 'results', 'user_costs')

data <-
  read.csv(file.path(folder_inputs, 'total_cost_estimates.csv'))

data <- data[(data$confidence == 50), ]

data = data[!grepl("psb", data$strategy), ]
data = data[!grepl("moran", data$strategy), ]
data = data[!grepl("srn", data$strategy), ]

data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'High Adoption'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline Adoption'
data$scenario_adopt[grep("low", data$scenario)] = 'Low Adoption'
data$scenario_adopt = factor(data$scenario_adopt,
                             levels = c("Low Adoption",
                                        "Baseline Adoption",
                                        "High Adoption"))

data$scenario_capacity = ''
data$scenario_capacity[grep("10_10_10", data$scenario)] = '10 GB/Month'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 GB/Month'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30 GB/Month'

data$strategy_short = ""
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("3G_epc_fiber", data$strategy)] = '3G (F)'
data$strategy_short[grep("3G_epc_wireless", data$strategy)] = '3G (W)'


data <-
  select(
    data,
    scenario_adopt,
    scenario_capacity,
    strategy_short,
    input_cost,
    total_private_cost,
    total_government_cost,
    total_financial_cost
  )

data = data %>% distinct(
  scenario_adopt,
  scenario_capacity,
  strategy_short,
  input_cost,
  total_private_cost,
  total_government_cost,
  total_financial_cost
)


data$scenario_capacity = factor(data$scenario_capacity,
                                levels = c("10 GB/Month",
                                           "20 GB/Month",
                                           "30 GB/Month"))

data <- data[(!data$scenario_capacity == '20 GB/Month'), ]

min_value = min(round(data$total_government_cost / 1e3, 2))
max_value = max(round(data$total_private_cost / 1e3, 2))

colnames(data)[colnames(data) == 'total_private_cost'] <-
  'Private Cost ($USD)'
colnames(data)[colnames(data) == 'total_government_cost'] <-
  'Government Cost ($USD)'

data <- data %>% gather(key = "Cost_Type",
                        value = "value",
                        'Private Cost ($USD)',
                        'Government Cost ($USD)',)

data$value = round(data$value / 1e3, 2)

data = select(
  data,
  scenario_adopt,
  scenario_capacity,
  strategy_short,
  input_cost,
  Cost_Type,
  value
)

data = spread(data, input_cost, value)

ggplot(data,
       aes(
         x = strategy_short,
         y = baseline,
         group = Cost_Type,
         fill = Cost_Type
       )) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(
    data = data,
    aes(y = baseline, ymin = low, ymax = high),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  coord_flip() +
  scale_fill_manual(values = c("#E1BE6A", "#40B0A6"), name = NULL) +
  theme(legend.position = "bottom") +
  labs(
    title = "Financial Cost of Universal Broadband Across Africa by Technology",
    colour = NULL,
    subtitle = "Interval bars reflect estimates for low and high cost scenarios",
    x = NULL,
    y = "Financial Cost (Trillions $USD)"
  ) +
  scale_y_continuous(expand = c(0, 0),
                     limits = c(min_value, max_value)) +
  guides(fill = guide_legend(ncol = 3, reverse = TRUE)) +
  facet_grid(scenario_capacity ~ scenario_adopt)

path = file.path(folder,
                 'figures',
                 'f_total_financial_cost_across_Africa.png')
ggsave(
  path,
  units = "in",
  width = 8,
  height = 5,
  dpi = 300
)
dev.off()
