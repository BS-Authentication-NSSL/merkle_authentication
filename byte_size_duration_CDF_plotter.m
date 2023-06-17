% Read the CSV file
data = readtable('byte_size_duration.csv');

% Define unique byte sizes
byte_sizes = [8, 16, 32, 64, 128, 256];

% Create a new figure
figure; hold on;

% Generate color map
colorMap = flipud(parula(length(byte_sizes)));

% Generate and plot CDF for each byte size
h = zeros(length(byte_sizes), 1);  % Placeholder for legend items
for i = 1:length(byte_sizes)
    size = byte_sizes(i);
    durations = data{data{:,1} == size, 2};
    
    % Skip if no data for this size
    if isempty(durations)
        continue;
    end
    
    % Sort data
    sorted_data = sort(durations);
    yvals = (1:length(sorted_data))/length(sorted_data);
    
    % Plot CDF
    h(i) = plot(sorted_data, yvals, 'LineWidth', 2, 'Color', colorMap(i, :)); 

    % Add vertical line for average
    avg = mean(durations);
    line([avg, avg], get(gca, 'ylim'), 'Color', colorMap(i, :), 'LineStyle', '--', 'LineWidth', 2);
end

% Set grid and labels
grid on; 
set(gca, 'XMinorGrid', 'on', 'YMinorGrid', 'off'); % Minor grid only on x-axis

% Set axis to be square
pbaspect([1 1 1]);

% Set font size
set(gca, 'FontSize', 16);

% Set labels
xlabel('Duration (ms)', 'FontSize', 16);
ylabel('CDF', 'FontSize', 16);

% Add legend
legend(h(h~=0), strcat(cellstr(num2str(byte_sizes(h~=0)')), ' B'), 'Location', 'southeast');

hold off;
