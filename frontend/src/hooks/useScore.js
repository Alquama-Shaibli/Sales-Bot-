// hooks/useScore.js — Manages lead scoring state
import { useState, useCallback } from 'react';
import api from './useApi';

export function useScore() {
  const [scoreData, setScoreData]   = useState(null);
  const [isScoring, setIsScoring]   = useState(false);
  const [scoreError, setScoreError] = useState(null);
  const [isQualifying, setIsQualifying] = useState(false);
  const [qualifyResult, setQualifyResult] = useState(null);

  // Trigger scoring for a completed conversation
  const scoreConversation = useCallback(async (conversationId) => {
    if (!conversationId || isScoring) return;

    setIsScoring(true);
    setScoreError(null);
    setScoreData(null);

    try {
      const { data } = await api.post('/api/score', { conversation_id: conversationId });
      setScoreData(data);
      return data;
    } catch (err) {
      setScoreError(err.message);
      return null;
    } finally {
      setIsScoring(false);
    }
  }, [isScoring]);

  // Qualify the lead and sync to HubSpot
  const qualifyLead = useCallback(async (conversationId, leadInfo) => {
    if (!conversationId || !scoreData) return;

    setIsQualifying(true);
    try {
      const payload = {
        conversation_id: conversationId,
        score: scoreData.overall_score,
        icp_fit: scoreData.breakdown.icp_fit,
        intent_level: scoreData.overall_score >= 70 ? 'High' : scoreData.overall_score >= 40 ? 'Medium' : 'Low',
        ...leadInfo,
      };
      const { data } = await api.post('/api/lead/qualify', payload);
      setQualifyResult(data);
      return data;
    } catch (err) {
      setScoreError(err.message);
      return null;
    } finally {
      setIsQualifying(false);
    }
  }, [scoreData]);

  // Helper: get color based on score
  const getScoreColor = useCallback((score) => {
    if (score >= 75) return '#ef4444';   // red — hot
    if (score >= 50) return '#f59e0b';   // amber — warm
    return '#3b82f6';                     // blue — cold
  }, []);

  const getScoreGradient = useCallback((score) => {
    if (score >= 75) return 'linear-gradient(90deg, #ef4444, #f59e0b)';
    if (score >= 50) return 'linear-gradient(90deg, #f59e0b, #fbbf24)';
    return 'linear-gradient(90deg, #3b82f6, #06b6d4)';
  }, []);

  const getScoreLabel = useCallback((score) => {
    if (score >= 75) return { label: '🔴 Hot Lead', badge: 'badge-hot', action: 'Route to Sales' };
    if (score >= 50) return { label: '🟡 Warm Lead', badge: 'badge-warm', action: 'Add to Nurture' };
    return { label: '🔵 Cold Lead', badge: 'badge-cold', action: 'Marketing Only' };
  }, []);

  const resetScore = useCallback(() => {
    setScoreData(null);
    setScoreError(null);
    setQualifyResult(null);
  }, []);

  return {
    scoreData,
    isScoring,
    scoreError,
    isQualifying,
    qualifyResult,
    scoreConversation,
    qualifyLead,
    getScoreColor,
    getScoreGradient,
    getScoreLabel,
    resetScore,
  };
}
