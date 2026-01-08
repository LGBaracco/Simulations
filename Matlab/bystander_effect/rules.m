function [ fncs ] = rules()
    % DO NOT EDIT
    fncs = l2.getRules();
    for i=1:length(fncs)
        fncs{i} = str2func(fncs{i});
    end
end

%ADD RULES BELOW

%DDR1 From desire of form of assisatnce to desire of interpetation of
%situation = emergency
function result = ddr1( trace, ~, t )

    result = {};
    
    for desire = l2.getall(trace, t, 'desire', {NaN, NaN})
         desire_type = desire.arg{2};
         agent = desire.arg{1};
         
         if strcmp(desire_type.name, 'form_of_assistance')
             situation = predicate('interpretation_of_situation', {'emergency'});
             result = {result{:} {t+1, 'desire', {agent, situation}}};
         end
    end
end

%DDR2 from desire of an interpretation fo emergency to a desire for sending
%a message
function result = ddr2( trace, ~, t )

    result = {};
    
    for desire = l2.getall(trace, t, 'desire', {NaN, NaN})
         desire_type = desire.arg{2};
         agent = desire.arg{1};
         
         if strcmp(desire_type.name, 'interpretation_of_situation')
             message = predicate('sending_a_message', {true});
             result = {result{:} {t+1, 'desire', {agent, message}}};
         end
    end
end

%DDR3 from desire of an interpretation fo emergency to a desire for sending
%a message
function result = ddr3( trace, ~, t )

    result = {};
    
    for desire = l2.getall(trace, t, 'desire', {NaN, NaN})
         desire_type = desire.arg{2};
         agent = desire.arg{1};
         
         if strcmp(desire_type.name, 'sending_a_message')
             message = predicate('sending_a_message', {true});
             result = {result{:} {t+1, 'proposal', {agent, message}}};
         end
    end
end

