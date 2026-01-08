function [ fncs ] = rules()
    % DO NOT EDIT
    fncs = l2.getRules();
    for i=1:length(fncs)
        fncs{i} = str2func(fncs{i});
    end
end

%ADD RULES BELOW

%DDR1 From observation to belief
function result = ddr1( trace, params, t )

    result = {};
    
    for observation = l2.getall(trace, t, 'observation', {NaN, NaN})
         observation_type = observation.arg{2};
         agent = observation.arg{1};
         belief = predicate('belief', {agent, observation_type});
         
         result = {result{:} {t+1, belief}};
    end
end

% Generates a belief of feeling of loneliness
function result = ddr2(trace, params, t)
    result = {};
    
    
    for belief_diseases = l2.getall(trace, t, 'belief', {NaN, NaN}) 
        
        if strcmp(belief_diseases.arg{2}.name, 'cardiovascular_diseases')
            for belief_performance = l2.getall(trace, t, 'belief', {NaN, NaN}) 
                
                if strcmp(belief_performance.arg{2}.name, 'performance') & ...
                        predcmp(belief_diseases.arg{1}, belief_performance.arg{1})
                    
                    agent = belief_diseases.arg{1};
                    
                    if strcmp(belief_performance.arg{2}.arg{1}, params.performance_for_loneliness) & ... 
                            belief_diseases.arg{2}.arg{1} == params.diseases_for_loneliness
                        
                        is_lonely = true;
                    else
                        is_lonely = false;
                    end

                    feeling_of_loneliness = predicate('feeling_of_loneliness', is_lonely);

                    result = {result{:} {t+1, 'belief', {agent, feeling_of_loneliness}}};
                    
                end
            end
        end
    end
end

function result = ddr3( trace, params, t )

    result = {};
    
    for desire = l2.getall(trace, t, 'desire', {NaN, NaN})
        
        for belief_loneliness = l2.getall(trace, t, 'belief', {NaN, NaN})
            
            if strcmp(belief_loneliness.arg{2}.name, 'feeling_of_loneliness') & ...
                    predcmp(belief_loneliness.arg{1}, desire.arg{1})
                
                if desire.arg{2}.arg{1}

                    desired = predicate('desirable', belief_loneliness.arg{2});
                    assessment = predicate('assessment', {desire.arg{1}, desired});
                    
                else
                    undesired = predicate('undesirable', belief_loneliness.arg{2});
                    assessment = predicate('assessment', {desire.arg{1}, undesired});
                    
                end
                result = {result{:} {t+1, assessment}};
            end
        end
    end
end




