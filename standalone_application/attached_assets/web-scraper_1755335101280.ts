import axios from 'axios';
import * as cheerio from 'cheerio';
import { storage } from '../storage';

interface ScrapedData {
  source: string;
  data: any;
  timestamp: number;
  confidence: number;
}

export class WebScraper {
  private scrapingQueue: string[] = [];
  private isActive = false;
  private lastScrapeTime = 0;
  private rateLimitDelay = 2000; // 2 seconds between requests

  constructor() {
    this.initializeTargets();
    this.startAutomaticScraping();
  }

  private initializeTargets(): void {
    // Initialize scraping targets for Pet Simulator 99 and gaming data
    this.scrapingQueue = [
      'https://www.roblox.com/games/8737899170/Pet-Simulator-99',
      'https://biggames.io/pet-simulator-99',
      'https://discord.gg/biggames',
      'https://twitter.com/BigGames_Roblox',
      'https://reddit.com/r/PetSimulatorX',
      'https://wiki.pet-simulator.com'
    ];
  }

  private async startAutomaticScraping(): Promise<void> {
    if (this.isActive) return;
    this.isActive = true;

    // Scrape every 5 minutes
    setInterval(async () => {
      await this.performScraping();
    }, 300000);

    console.log('Web scraper activated for intelligent data gathering');
  }

  private async performScraping(): Promise<void> {
    try {
      for (const url of this.scrapingQueue) {
        await this.scrapeURL(url);
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, this.rateLimitDelay));
      }
    } catch (error) {
      console.log('Scraping cycle error:', error);
    }
  }

  private async scrapeURL(url: string): Promise<ScrapedData | null> {
    try {
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1'
        },
        timeout: 10000
      });

      const $ = cheerio.load(response.data);
      let scrapedData: any = {};

      // Extract relevant data based on URL
      if (url.includes('roblox.com')) {
        scrapedData = await this.scrapeRobloxGamePage($);
      } else if (url.includes('biggames.io')) {
        scrapedData = await this.scrapeBigGamesPage($);
      } else if (url.includes('discord.gg')) {
        scrapedData = await this.scrapeDiscordInvite($);
      } else if (url.includes('reddit.com')) {
        scrapedData = await this.scrapeRedditData($);
      } else {
        scrapedData = await this.scrapeGenericGameData($);
      }

      const result: ScrapedData = {
        source: url,
        data: scrapedData,
        timestamp: Date.now(),
        confidence: 0.85
      };

      // Store scraped data in learning materials
      await storage.createLearningMaterial({
        userId: 1,
        name: `Scraped Data: ${new URL(url).hostname}`,
        content: JSON.stringify(result, null, 2),
        type: 'scraped_data'
      });

      console.log(`Successfully scraped: ${url}`);
      return result;

    } catch (error) {
      console.log(`Failed to scrape ${url}: ${error.message}`);
      return null;
    }
  }

  private async scrapeRobloxGamePage($: cheerio.CheerioAPI): Promise<any> {
    return {
      type: 'roblox_game',
      title: $('h1[data-testid="game-name"]').text().trim(),
      description: $('p[data-testid="game-description"]').text().trim(),
      playerCount: $('[data-testid="player-count"]').text().trim(),
      rating: $('[data-testid="game-rating"]').text().trim(),
      updates: $('[data-testid="game-updates"] .text-description').map((_, el) => $(el).text().trim()).get(),
      badges: $('[data-testid="game-badges"] .badge-name').map((_, el) => $(el).text().trim()).get(),
      scraped_at: new Date().toISOString()
    };
  }

  private async scrapeBigGamesPage($: cheerio.CheerioAPI): Promise<any> {
    return {
      type: 'biggames_official',
      title: $('title').text().trim(),
      news: $('.news-item, .update-item').map((_, el) => ({
        title: $(el).find('.title, h3').text().trim(),
        content: $(el).find('.content, p').text().trim(),
        date: $(el).find('.date').text().trim()
      })).get(),
      events: $('.event-item').map((_, el) => ({
        name: $(el).find('.event-name').text().trim(),
        description: $(el).find('.event-description').text().trim(),
        endDate: $(el).find('.event-end').text().trim()
      })).get(),
      scraped_at: new Date().toISOString()
    };
  }

  private async scrapeDiscordInvite($: cheerio.CheerioAPI): Promise<any> {
    return {
      type: 'discord_community',
      serverName: $('h1, .server-name').text().trim(),
      memberCount: $('[data-testid="member-count"], .member-count').text().trim(),
      onlineCount: $('[data-testid="online-count"], .online-count').text().trim(),
      description: $('meta[name="description"]').attr('content') || '',
      scraped_at: new Date().toISOString()
    };
  }

  private async scrapeRedditData($: cheerio.CheerioAPI): Promise<any> {
    return {
      type: 'reddit_community',
      posts: $('[data-testid="post"], .Post').slice(0, 10).map((_, el) => ({
        title: $(el).find('[data-testid="post-content"] h3, .Post-title').text().trim(),
        author: $(el).find('[data-testid="author-link"], .Post-author').text().trim(),
        score: $(el).find('[data-testid="upvote-button"], .Post-score').text().trim(),
        comments: $(el).find('[data-testid="comment-count"], .Post-comments').text().trim(),
        time: $(el).find('[data-testid="post-timestamp"], .Post-time').text().trim()
      })).get(),
      scraped_at: new Date().toISOString()
    };
  }

  private async scrapeGenericGameData($: cheerio.CheerioAPI): Promise<any> {
    return {
      type: 'generic_game_data',
      title: $('title').text().trim(),
      headings: $('h1, h2, h3').map((_, el) => $(el).text().trim()).get().slice(0, 10),
      links: $('a[href*="pet"], a[href*="simulator"], a[href*="game"]').map((_, el) => ({
        text: $(el).text().trim(),
        href: $(el).attr('href')
      })).get().slice(0, 20),
      images: $('img[alt*="pet"], img[alt*="simulator"], img[src*="pet"]').map((_, el) => ({
        alt: $(el).attr('alt'),
        src: $(el).attr('src')
      })).get().slice(0, 10),
      keywords: this.extractKeywords($('body').text()),
      scraped_at: new Date().toISOString()
    };
  }

  private extractKeywords(text: string): string[] {
    const gameKeywords = [
      'pet simulator', 'huge', 'titanic', 'shiny', 'rainbow', 'exclusive',
      'egg', 'hatch', 'luck', 'boost', 'biggames', 'update', 'event',
      'trading', 'value', 'rare', 'legendary', 'mythical', 'chest',
      'slime tycoon', 'breakable', 'damage', 'automation', 'script'
    ];

    const foundKeywords = [];
    const lowerText = text.toLowerCase();

    for (const keyword of gameKeywords) {
      if (lowerText.includes(keyword)) {
        foundKeywords.push(keyword);
      }
    }

    return foundKeywords;
  }

  // Public methods for specific scraping tasks
  async scrapePS99Data(): Promise<any> {
    try {
      const ps99Urls = [
        'https://www.roblox.com/games/8737899170/Pet-Simulator-99',
        'https://biggames.io/pet-simulator-99'
      ];

      const results = [];
      for (const url of ps99Urls) {
        const data = await this.scrapeURL(url);
        if (data) results.push(data);
      }

      return {
        sources: results.length,
        data: results,
        aggregated_at: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`PS99 data scraping failed: ${error.message}`);
    }
  }

  async scrapeGameUpdates(): Promise<any> {
    try {
      const updateSources = [
        'https://biggames.io/pet-simulator-99',
        'https://discord.gg/biggames',
        'https://twitter.com/BigGames_Roblox'
      ];

      const updates = [];
      for (const url of updateSources) {
        const data = await this.scrapeURL(url);
        if (data?.data?.news || data?.data?.updates) {
          updates.push({
            source: url,
            updates: data.data.news || data.data.updates || []
          });
        }
      }

      return {
        total_sources: updates.length,
        updates: updates,
        scraped_at: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Game updates scraping failed: ${error.message}`);
    }
  }

  async scrapeTradingValues(): Promise<any> {
    try {
      // Scrape trading value websites
      const tradingUrls = [
        'https://reddit.com/r/PetSimulatorX',
        'https://discord.gg/biggames'
      ];

      const tradingData = [];
      for (const url of tradingUrls) {
        const data = await this.scrapeURL(url);
        if (data) tradingData.push(data);
      }

      return {
        sources: tradingData.length,
        trading_data: tradingData,
        last_updated: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Trading values scraping failed: ${error.message}`);
    }
  }

  async intelligentSearch(query: string): Promise<any> {
    try {
      // Perform intelligent web search for specific game information
      const searchUrls = [
        `https://www.google.com/search?q=site:reddit.com "${query}" pet simulator 99`,
        `https://www.google.com/search?q=site:discord.gg "${query}" biggames`,
        `https://www.google.com/search?q="${query}" pet simulator 99 guide`
      ];

      const searchResults = [];
      for (const url of searchUrls.slice(0, 1)) { // Limit to avoid rate limits
        try {
          const data = await this.scrapeURL(url);
          if (data) searchResults.push(data);
        } catch (error) {
          console.log(`Search failed for: ${url}`);
        }
      }

      return {
        query: query,
        results: searchResults,
        searched_at: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Intelligent search failed: ${error.message}`);
    }
  }

  getScrapingStats(): any {
    return {
      active: this.isActive,
      queue_size: this.scrapingQueue.length,
      last_scrape: new Date(this.lastScrapeTime).toISOString(),
      rate_limit_delay: this.rateLimitDelay
    };
  }
}

export const webScraper = new WebScraper();